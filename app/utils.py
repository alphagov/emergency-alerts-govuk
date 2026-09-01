import contextlib
import hashlib
import io
import json
import os
import re
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests
from dateutil.parser import parse as dt_parse
from flask import current_app
from markupsafe import Markup, escape

from app import version
from app.models.publish_task_progress import update_publish_progress_if_exists

REPO = Path(__file__).parent.parent
DIST = REPO / 'dist'
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ARCHIVE_FILENAME = "archive_govuk-alerts-website.tar.gz"


def capitalise(value):
    return value[0].upper() + value[1:]


def simplify_custom_area_name(value, language):
    if not is_custom_area_with_local_authority(value):
        return value
    local_authority = get_local_authority_from_custom_area(value)
    if language == 'cy':
        return f"ardal yn {local_authority}"
    elif language == 'en':
        return f"an area in {local_authority}"


def get_local_authority_from_custom_area(value):
    if is_custom_area_with_local_authority(value):
        return value.split(" in ")[1]


def is_custom_area_with_local_authority(value):
    return (
        (
            'postcode' in value
            or 'easting' in value
            or 'latitude' in value
        ) and (" in " in value)
    )


def paragraphize(value, classes="govuk-body govuk-!-margin-bottom-4", truncate=False, escape_content=True):
    if escape_content:
        value = escape(value)
    if truncate:
        paragraphs = f'<p class="{classes} truncated-text">{value}</p>'
        return Markup(paragraphs)
    else:
        paragraphs = [
            f'<p class="{classes}">{line}</p>'
            for line in value.split('\n')
            if line
        ]
        return Markup('\n\n'.join(paragraphs))


def file_fingerprint(path, root=DIST):
    path = Path(path).relative_to('/')  # path comes in as absolute, rooted to the dist folder
    path_regex = re.compile(f'^{path.stem}-[0-9a-z]{{8}}{path.suffix}$')  # regexp based on the filename + a 8 char hash
    matches = [
                filename for filename
                in os.listdir(str(root / path.parent))
                if path_regex.search(filename)]

    if len(matches) == 0:
        raise OSError(f'{str(root / path.parent / path.stem)}-[hash]{path.suffix} referenced but not available')

    return f'/{path.parent}/{matches[0]}'


def is_in_uk(simple_polygons):
    uk_south_west = [49.240, -9.279]  # random map point
    uk_north_east = [61.456, 3.007]  # random map point

    first_polygon = simple_polygons[0]
    first_coordinate = first_polygon[0]

    return (
        first_coordinate[0] > uk_south_west[0] and
        first_coordinate[0] < uk_north_east[0] and
        first_coordinate[1] > uk_south_west[1] and
        first_coordinate[1] < uk_north_east[1]
    )


def setup_boto3_session():
    host_environment = current_app.config["HOST"]
    if host_environment == "hosted":
        session = boto3.Session()
    else:
        session = boto3.Session(
            aws_access_key_id=current_app.config["BROADCASTS_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["BROADCASTS_AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_REGION"],
        )
    return session


def setup_s3_session():
    session = setup_boto3_session()
    return session.client('s3')


def setup_ssm_session():
    session = setup_boto3_session()
    return session.client('ssm')


def upload_html_to_s3(rendered_pages, publish_destination, publish_task_progress=None):
    if publish_destination is None:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    s3 = setup_s3_session()
    files_to_upload = []

    for path, content in rendered_pages.items():
        current_app.logger.info("Uploading " + path + " to " + publish_destination)
        content_type = "text/xml" if path.endswith(".atom") else "text/html"

        files_to_upload.append({
            "key": path,
            "data": content,
            "content_type": content_type,
        })

        update_publish_progress_if_exists(publish_task_progress, path)

    _upload_files_threaded(s3, publish_destination, files_to_upload)


def upload_assets_to_s3(publish_task_progress, publish_destination):
    if publish_destination is None:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    s3 = setup_s3_session()
    files_to_upload = []

    assets = get_asset_files()
    for filename, (content, mimetype) in assets.items():
        current_app.logger.info("Uploading " + filename + " to " + publish_destination)
        files_to_upload.append({
            "key": filename,
            "data": content,
            "content_type": mimetype,
        })
        publish_task_progress.update_progress(file=filename)

    _upload_files_threaded(s3, publish_destination, files_to_upload)

    return assets


def upload_cap_xml_to_s3(cap_xml_alerts, publish_destination, publish_task_progress):
    if publish_destination is None:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    s3 = setup_s3_session()
    files_to_upload = []

    for path, content in cap_xml_alerts.items():
        current_app.logger.info("Uploading " + path + " to " + publish_destination)

        files_to_upload.append({
            "key": path,
            "data": content,
            "content_type": "application/cap+xml",
        })

        publish_task_progress.update_progress(file=path)

    _upload_files_threaded(s3, publish_destination, files_to_upload)


def purge_fastly_cache():
    if not current_app.config["FASTLY_ENABLED"]:
        current_app.logger.info("Skipping Fastly as FASTLY_ENABLED=false")
        return

    fastly_service_id = current_app.config["FASTLY_SERVICE_ID"]
    fastly_api_key = current_app.config["FASTLY_API_KEY"]
    surrogate_key = current_app.config["FASTLY_SURROGATE_KEY"]
    fastly_url = f"https://api.fastly.com/service/{fastly_service_id}/purge/{surrogate_key}"

    headers = {
        "Accept": "application/json",
        "Fastly-Key": f"{fastly_api_key}"
    }
    current_app.logger.info("Purging cache")

    resp = requests.post(fastly_url, headers=headers)
    resp.raise_for_status()


def generate_content_manifest(rendered_pages, publish_destination):
    """
    Generates a content manifest containing SHA-256 hashes of the mutable pages
    that are affected by alert submissions/cancellations: the index page, current-alerts,
    and past-alerts.

    This manifest is used for two things:
    1. Origin switch verification during publish (checking the 'origin' field
       matches the expected destination bucket)
    2. Ongoing cache integrity monitoring (the ability to compare a content hash taken
       externally to the content has we stick in the manifest that represents what we
       "expect" to see).
    """
    mutable_page_keys = ["alerts", "alerts/current-alerts", "alerts/past-alerts"]

    page_hashes = {}
    for key in mutable_page_keys:
        content = rendered_pages.get(key)
        if content is not None:
            if isinstance(content, str):
                content = content.encode("utf-8")
            page_hashes[key] = hashlib.sha256(content).hexdigest()

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "origin": publish_destination,
        "pages": page_hashes,
    }

    return json.dumps(manifest, indent=2)


def upload_content_manifest(manifest, publish_destination):
    """
    Uploads the content manifest to the destination bucket with Cache-Control headers
    that prevent downstream caching (i.e., by Fastly). This ensures the manifest
    is always fetched fresh from S3.

    This should be used to push the content manifest into the destination bucket (that
    traffic is being switched over to) so we can verify traffic has been properly rerouted
    before purging any caches.
    """
    if publish_destination is None:
        current_app.logger.info("Target S3 bucket not specified: Skipping manifest upload")
        return

    s3 = setup_s3_session()
    s3.put_object(
        Bucket=publish_destination,
        Key="_content-manifest",
        Body=manifest.encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-cache, no-store, must-revalidate",
    )
    current_app.logger.info(f"Uploaded content manifest to {publish_destination}")


def upload_content_manifest_to_both_buckets(manifest):
    """
    Uploads the content manifest to both blue and green buckets.
    This can be used to ensure both origins have a representative hash of the expected
    content, regardless of where CloudFront may be routing traffic.
    """
    s3 = setup_s3_session()
    blue_bucket = current_app.config["GOVUK_ALERTS_BLUE_S3_BUCKET_NAME"]
    green_bucket = current_app.config["GOVUK_ALERTS_GREEN_S3_BUCKET_NAME"]

    for bucket in (blue_bucket, green_bucket):
        if not bucket:
            continue
        s3.put_object(
            Bucket=bucket,
            Key="_content-manifest",
            Body=manifest.encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-cache, no-store, must-revalidate",
        )

    current_app.logger.info("Uploaded content manifest to both buckets")


def get_asset_files():
    folder = DIST

    if not Path(folder).exists():
        raise FileExistsError(f'Folder {folder} not found.')

    assets = {}

    for root, _, files in os.walk(folder):
        s3path = root[root.find("alerts/"):]

        # ignore hidden files and folders
        files = [f for f in files if not f[0] == "."]

        for file in files:
            filename = root + "/" + file
            s3name = s3path + "/" + file
            mode = "r" if file[-3:] == "css" or file[-2:] == "js" else "rb"
            with open(filename, mode) as f:
                contents = f.read()
                mime_type = mimetype_from_extension[file.split(".")[-1]]
                assets[s3name] = (contents, mime_type)

    return assets


mimetype_from_extension = {
    "html": "text/html",
    "css": "text/css",
    "ico": "image/x-icon",
    "jpg": "image/jpeg",
    "js": "application/javascript",
    "map": "application/javascript",
    "png": "image/png",
    "svg": "image/svg+xml",
    "webp": "image/webp",
    "woff": "font/woff",
    "woff2": "font/woff2",
}


def post_version_to_cloudwatch():
    try:
        boto3.client(
            "cloudwatch", region_name=current_app.config["AWS_REGION"]
        ).put_metric_data(
            MetricData=[
                {
                    "MetricName": "AppVersion",
                    "Dimensions": [
                        {
                            "Name": "Application",
                            "Value": "govuk",
                        },
                        {
                            "Name": "Version",
                            "Value": version.app_version,
                        },
                    ],
                    "Unit": "Count",
                    "Value": 1,
                }
            ],
            Namespace="Emergency Alerts",
        )
    except Exception:
        current_app.logger.exception(
            "Couldn't post app version to CloudWatch. App version: %s",
        )


def create_cap_event(alert, identifier, url=None, cancelled=False, prev_alert_identifier=None):
    cap_dict = {
        "identifier": identifier,
        "message_type": "cancel" if cancelled else "alert",
        "message_format": "cap",
        "headline": "GOV.UK Emergency alert",
        "description": alert.content,
        "language": "en",
        "areas": [{
            "polygons": [polygons for polygons in alert.areas.get("simple_polygons")],
            **({"description": alert.display_areas_formatted_string} if alert.display_areas else {})
        }],
        "channel": "severe",
        "sent": alert.starts_at.isoformat(timespec="seconds"),
        "expires": (
            alert.cancelled_at.isoformat(timespec="seconds")
            if cancelled
            else alert.finishes_at.isoformat(timespec="seconds")
        ),
        "web": url,
    }

    if cancelled:
        cap_dict["references"] = [
            {
                "message_id": prev_alert_identifier,
                "sent": alert.starts_at.isoformat(timespec="seconds"),
            }
        ]
    return cap_dict


def create_publish_progress_task_id(publish_type, publish_origin):
    return f"{publish_type}_{publish_origin}_{int(time.time())}"


def archive_website(html, capxml, assets=None):
    dest_bucket = current_app.config["GOVUK_ALERTS_ARCHIVE_S3_BUCKET_NAME"]
    if not dest_bucket:
        current_app.logger.info("Target S3 bucket not specified: Skipping archive")
        return current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]

    if not assets:
        assets = get_asset_files()

    published_files = html | capxml | assets

    s3 = setup_s3_session()

    # Same tar will be created every time, dest_bucket will have versioning enabled.
    tar_file = ARCHIVE_FILENAME

    buffer = io.BytesIO()

    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for key, content in published_files.items():

            # If content is a (bytes, mimetype) tuple, extract the bytes
            if isinstance(content, tuple):
                content = content[0]

            # Convert str → bytes
            if isinstance(content, str):
                content = content.encode()

            if key == "alerts":
                tar_name = "alerts.html"
            else:
                tar_name = key

            info = tarfile.TarInfo(name=tar_name)
            info.size = len(content)

            tar.addfile(info, io.BytesIO(content))

    buffer.seek(0)
    s3.upload_fileobj(buffer, dest_bucket, tar_file)


def get_publish_destination():
    current_bucket_param = current_app.config["GOVUK_ALERTS_CURRENT_BUCKET_PARAM"]
    ssm = setup_ssm_session()
    try:
        response = ssm.get_parameter(Name=current_bucket_param)
        value = response["Parameter"]["Value"].strip().lower()
    except Exception as e:
        raise RuntimeError(
            f"Failed to read SSM parameter '{current_bucket_param}': {e}"
        )

    if value == current_app.config["GOVUK_ALERTS_BLUE_S3_BUCKET_NAME"]:
        # Currently pointing to blue bucket, so return green as destination
        return current_app.config["GOVUK_ALERTS_GREEN_S3_BUCKET_NAME"]

    if value == current_app.config["GOVUK_ALERTS_GREEN_S3_BUCKET_NAME"]:
        # Currently pointing to green bucket, so return blue as destination
        return current_app.config["GOVUK_ALERTS_BLUE_S3_BUCKET_NAME"]

    # Invalid value - log and return nothing
    raise ValueError(
        f"Invalid SSM value '{value}' for '{current_bucket_param}'. Expected 'blue' or 'green'."
    )


def prepare_destination(publish_bucket):
    s3 = setup_s3_session()

    try:
        objects_to_delete = []

        # Paginate through all objects
        paginator = s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=publish_bucket):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                objects_to_delete.append({"Key": key})

                # Delete in batches of 1000 (S3 API limit)
                if len(objects_to_delete) == 1000:
                    s3.delete_objects(Bucket=publish_bucket, Delete={"Objects": objects_to_delete})
                    objects_to_delete = []

        # Delete any remaining objects
        if objects_to_delete:
            s3.delete_objects(Bucket=publish_bucket, Delete={"Objects": objects_to_delete})

    except Exception as e:
        raise RuntimeError(
            f"Failed to delete files from publish destination '{publish_bucket}': {e}"
        )


def restore_latest_archive(publish_bucket):
    s3 = setup_s3_session()
    current_member = None
    files_to_upload = []

    try:
        # Retrieve latest archive from archive bucket and extract contents into publish bucket
        timestamp, body = _get_latest_govuk_archive(s3)

        with tarfile.open(fileobj=body, mode="r:gz") as tar:
            for member in tar.getmembers():
                current_member = member.name

                if not member.isfile():
                    continue

                extracted = tar.extractfile(member)
                if extracted is None:
                    continue

                data = extracted.read()
                key = "alerts" if member.name == "alerts.html" else member.name

                files_to_upload.append({
                    "key": key,
                    "data": data,
                    "content_type": _get_mime_type(key),
                })

        _upload_files_threaded(s3, publish_bucket, files_to_upload)

    except Exception as e:
        raise RuntimeError(
            f"Failed to restore files from archive to '{publish_bucket}'. "
            f"Error occurred while processing: {current_member}. "
            f"Original error: {e}"
        )


def _get_mime_type(name):
    if name.endswith(".cap.xml"):
        return "application/cap+xml"
    if name.endswith(".atom"):
        return "text/xml"
    if name.endswith(".cy") or name.endswith(".xsl"):
        return "text/html"

    parts = name.split(".")
    if len(parts) == 1:
        return "text/html"
    else:
        return mimetype_from_extension.get(parts[-1], "application/octet-stream")


def _get_latest_govuk_archive(s3):
    bucket = current_app.config["GOVUK_ALERTS_ARCHIVE_S3_BUCKET_NAME"]
    if not bucket:
        current_app.logger.info("Skipping retrieval of archive timestamp in local environment")
        raise RuntimeError("Archive bucket not configured")

    try:
        response = s3.head_object(Bucket=bucket, Key=ARCHIVE_FILENAME)
        timestamp = response["LastModified"]
        if isinstance(timestamp, str):
            timestamp = dt_parse(timestamp)
        obj = s3.get_object(Bucket=bucket, Key=ARCHIVE_FILENAME)
        raw = obj["Body"].read()
        archive = io.BytesIO(raw)
        current_app.logger.info(f"Retrieved archive with timestamp: {timestamp}")
        return timestamp, archive

    except Exception as e:
        current_app.logger.exception("Unable to retrieve archive file")
        raise RuntimeError(f"Unable to retrieve archive file: {e}")


def switch_destination(switch_to_bucket):
    """
    Updates the SSM parameter that determines which S3 origin serves traffic.
    An origin-request Lambda@Edge function reads this parameter to decide which
    bucket to route requests to, enabling what is effectively a rapid blue/green
    deployment mechanism.

    The SSM write is effectively immediate, but the origin-request Lambda@Edge may
    cache the value in its execution environment for a short window. It is therefore
    verified via the content manifest that the new origin is actually being served
    before returning (so the caller can safely purge our CDN cache, i.e., Fastly).
    """
    try:
        CLOUDFRONT_ENABLED = current_app.config["GOVUK_ALERTS_CLOUDFRONT_ENABLED"]

        if not CLOUDFRONT_ENABLED:
            current_app.logger.info(
                f"CloudFront not enabled, would be switching origin to {switch_to_bucket}"
            )
            _update_current_bucket_parameter(switch_to_bucket)
            return

        _update_current_bucket_parameter(switch_to_bucket)
        _wait_for_origin_switch(switch_to_bucket)

    except Exception as e:
        current_app.logger.exception("Unable to switch origin")
        raise RuntimeError(f"Unable to switch origin: {e}") from e


def _wait_for_origin_switch(expected_bucket, max_wait=30, interval=2):
    """
    Polls the content manifest through CloudFront to verify the origin switch has
    taken effect (i.e., the origin-request Lambda@Edge is now routing to the new
    bucket). Checks the 'origin' field in the manifest matches the expected bucket.
    Falls back to a fixed delay if the CloudFront URL is not configured.
    """
    cf_url = current_app.config.get("GOVUK_ALERTS_CLOUDFRONT_URL")

    if not cf_url:
        current_app.logger.info(
            "GOVUK_ALERTS_CLOUDFRONT_URL not configured, waiting 5s for origin switch"
        )
        time.sleep(5)
        return

    manifest_url = f"https://{cf_url}/_content-manifest"
    deadline = time.time() + max_wait

    while time.time() < deadline:
        with contextlib.suppress(Exception):
            resp = requests.get(manifest_url, timeout=5, headers={"Cache-Control": "no-cache"})
            if resp.status_code == 200:
                manifest_data = resp.json()
                if manifest_data.get("origin") == expected_bucket:
                    current_app.logger.info("Origin switch verified via content manifest")
                    return
        time.sleep(interval)

    current_app.logger.warning(
        {f"Origin switch verification timed out after {max_wait}s. Proceeding with Fastly purge."}
    )


def _update_current_bucket_parameter(current_bucket):
    current_bucket_param = current_app.config["GOVUK_ALERTS_CURRENT_BUCKET_PARAM"]
    current_app.logger.info(f"Updating SSM parameter {current_bucket_param} - setting to {current_bucket}")

    ssm = setup_ssm_session()

    try:
        ssm.put_parameter(
            Name=current_bucket_param,
            Value=current_bucket,
            Type="String",
            Overwrite=True,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to write SSM parameter '{current_bucket_param}': {e}"
        )


def _upload_files_threaded(s3, bucket, files, max_workers=8):
    """
    Upload multiple files to S3 concurrently.

    :param s3: boto3 S3 client
    :param bucket: target bucket name
    :param files: iterable of dicts: { "key": ..., "data": ..., "content_type": ... }
    :param max_workers: number of concurrent uploads
    """

    def upload_one(file):
        s3.put_object(
            Bucket=bucket,
            Key=file["key"],
            Body=file["data"],
            ContentType=file["content_type"],
        )
        return file["key"]

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(upload_one, f): f["key"] for f in files}

        for future in as_completed(futures):
            future.result()  # propagate exceptions
