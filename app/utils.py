import os
import re
from pathlib import Path

import boto3
import requests
from flask import current_app
from markupsafe import Markup, escape

REPO = Path(__file__).parent.parent
DIST = REPO / 'dist'


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


def upload_html_to_s3(rendered_pages, broadcast_event_id=""):
    host_environment = current_app.config["HOST"]

    bucket_name = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    if not bucket_name:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    if host_environment == "hosted":
        session = boto3.Session()
    else:
        session = boto3.Session(
            aws_access_key_id=current_app.config["BROADCASTS_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["BROADCASTS_AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_REGION"],
        )

    s3 = session.client('s3')

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


def upload_assets_to_s3():
    if not Path(DIST).exists():
        raise FileExistsError(f'Folder {DIST} not found.')

    bucket_name = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    if not bucket_name:
        current_app.logger.info("Target S3 bucket not specified: Skipping upload")
        return

    host_environment = os.environ.get('HOST')

    if host_environment == "hosted":
        session = boto3.Session()

    else:
        session = boto3.Session(
            aws_access_key_id=current_app.config["BROADCASTS_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["BROADCASTS_AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["BROADCASTS_AWS_REGION"],
        )
    s3 = session.client('s3')

    assets = get_asset_files(DIST)
    for filename, (content, mimetype) in assets.items():
        current_app.logger.info("Uploading " + filename)
        s3.put_object(
            Body=content,
            Bucket=bucket_name,
            ContentType=mimetype,
            Key=filename
        )


def purge_fastly_cache():
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
