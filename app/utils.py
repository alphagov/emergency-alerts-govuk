import os
import re
import time
from pathlib import Path

import boto3
import requests
from flask import current_app
from markupsafe import Markup, escape

from app import version

REPO = Path(__file__).parent.parent
DIST = REPO / 'dist'
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


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


def paragraphize(value, classes="govuk-body govuk-!-margin-bottom-4", truncate=False):
    if truncate:
        paragraphs = f'<p class="{classes} truncated-text">{value}</p>'
        return Markup(paragraphs)
    else:
        paragraphs = [
            f'<p class="{classes}">{line}</p>'
            for line in escape(value).split('\n')
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


def setup_s3_client():
    host_environment = current_app.config["HOST"]
    if host_environment == "hosted":
        session = boto3.Session()
    else:
        session = boto3.Session(
            aws_access_key_id=current_app.config["BROADCASTS_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["BROADCASTS_AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_REGION"],
        )
    return session.client('s3')


def upload_html_to_s3(rendered_pages, filename, broadcast_event_id=""):

    bucket_name = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    if not bucket_name:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    s3 = setup_s3_client()

    for path, content in rendered_pages.items():
        current_app.logger.info(
            "Uploading " + path,
            extra={
                "broadcast_event_id": broadcast_event_id
            }
        )
        content_type = "text/xml" if path.endswith(".atom") else "text/html"
        s3.put_object(
            Body=content,
            Bucket=bucket_name,
            ContentType=content_type,
            Key=path
        )
        put_timestamp_to_s3(filename, s3)


def upload_assets_to_s3(filename):
    if not Path(DIST).exists():
        raise FileExistsError(f'Folder {DIST} not found.')

    bucket_name = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    if not bucket_name:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    s3 = setup_s3_client()

    assets = get_asset_files(DIST)
    for filename, (content, mimetype) in assets.items():
        current_app.logger.info("Uploading " + filename)
        s3.put_object(
            Body=content,
            Bucket=bucket_name,
            ContentType=mimetype,
            Key=filename
        )
        put_timestamp_to_s3(filename, s3)


def upload_cap_xml_to_s3(cap_xml_alerts, filename, broadcast_event_id=""):

    bucket_name = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    if not bucket_name:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    s3 = setup_s3_client()

    for path, content in cap_xml_alerts.items():

        current_app.logger.info(
            "Uploading " + path,
            extra={
                "broadcast_event_id": broadcast_event_id
            }
        )

        s3.put_object(
            Body=content,
            Bucket=bucket_name,
            ContentType="application/cap+xml",
            Key=path
        )
        put_timestamp_to_s3(filename, s3)


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


def get_asset_files(folder):
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


def create_cap_event(alert, identifier, url=None, cancelled=False):
    return {
        "identifier": identifier,
        "message_type": "alert",
        "message_format": "cap",
        "headline": "GOV.UK Emergency alert",
        "description": alert.content,
        "language": "en-GB",
        "areas": [
            {
                "polygon": polygons,
            }
            for polygons in alert.areas.get("simple_polygons")
        ],
        "channel": "severe",
        "sent": alert.starts_at.isoformat(timespec="seconds"),
        "expires": (
            alert.cancelled_at.isoformat(timespec="seconds")
            if cancelled
            else alert.finishes_at.isoformat(timespec="seconds")
        ),
        "web": url,
    }


def put_timestamp_to_s3(filename, s3):
    publish_timestamps_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]
    s3.put_object(
        Body=f'{int(time.time())}',
        Bucket=publish_timestamps_bucket_name,
        ContentType="text/plain",
        Key=filename
    )


def delete_timestamp_file_from_s3(filename):
    publish_timestamps_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]
    host_environment = current_app.config["HOST"]

    if host_environment == "hosted":
        session = boto3.Session()
    else:
        session = boto3.Session(
            aws_access_key_id=current_app.config["BROADCASTS_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["BROADCASTS_AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_REGION"],
        )

    s3 = session.client('s3')
    s3.delete_object(
        Bucket=publish_timestamps_bucket_name,
        Key=filename,
    )
    current_app.logger.info(f"Deleted {filename}, publish successful")
