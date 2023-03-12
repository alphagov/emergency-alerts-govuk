import os
import re
from pathlib import Path

import boto3
import requests
from flask import current_app
from jinja2 import Markup, escape


REPO = Path(__file__).parent.parent
DIST = REPO / 'dist'


def paragraphize(value, classes="govuk-body-l govuk-!-margin-bottom-4"):
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


def upload_html_to_s3(rendered_pages):
    upload_to_s3(rendered_pages.items())


def upload_assets_to_s3():
    if not Path(DIST).exists():
        raise FileExistsError(f'Folder {DIST} not found.')

    assets = get_assets(DIST)

    s3 = boto3.client('s3')
    bucket_name = os.environ.get('GOVUK_ALERTS_S3_BUCKET_NAME')

    for localfile, s3path in assets.items():
        with open(localfile, 'rb') as data:
            s3.upload_fileobj(data, bucket_name, s3path)


def upload_to_s3(items):
    session = boto3.Session()

    s3 = session.resource('s3')
    bucket_name = os.environ.get('GOVUK_ALERTS_S3_BUCKET_NAME')

    for path, content in items:
        current_app.logger.info("Uploading " + path)
        item = s3.Object(bucket_name, path)
        item.put(Body=content)


def purge_fastly_cache():
    fastly_service_id = os.environ.get['FASTLY_SERVICE_ID']
    fastly_api_key = os.environ.get['FASTLY_API_KEY']
    surrogate_key = os.environ.get['FASTLY_SURROGATE_KEY']
    fastly_url = f"https://api.fastly.com/service/{fastly_service_id}/purge/{surrogate_key}"

    headers = {
        "Accept": "application/json",
        "Fastly-Key": f"{fastly_api_key}"
    }
    current_app.logger.info("Purging cache")

    resp = requests.post(fastly_url, headers=headers)
    resp.raise_for_status()


def get_assets(folder):
    assets = {}

    for root, _, files in os.walk(folder):
        s3path = root[root.find("alerts/"):]

        # ignore hidden files and folders
        files = [f for f in files if not f[0] == '.']

        for file in files:
            rootname = root + "/" + file
            print(rootname)

            s3name = s3path + "/" + file
            print(s3name)

            assets[rootname] = s3name

    return assets
