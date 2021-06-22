import logging
import os
import re
from pathlib import Path

import boto3
import requests
from jinja2 import Markup, escape

REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


logger = logging.getLogger()
logger.setLevel(logging.INFO)


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


def upload_to_s3(rendered_pages):
    s3 = boto3.resource('s3')
    bucket_name = os.environ['GOVUK_ALERTS_BUCKET_NAME']

    for path, content in rendered_pages.items():
        logger.info("Uploading " + path)
        item = s3.Object(bucket_name, path)
        item.put(Body=content, ContentType="text/html")


def purge_cache():
    fastly_service_id = os.environ['FASTLY_SERVICE_ID']
    fastly_api_key = os.environ['FASTLY_API_KEY']
    surrogate_key = os.getenv('GOVUK_ALERTS_FASTLY_SURROGATE_KEY', 'notify-emergency-alerts')
    fastly_url = f"https://api.fastly.com/{fastly_service_id}/purge/{surrogate_key}"

    headers = {
        "Accept": "application/json",
        "Fastly-Key": f"{fastly_api_key}"
    }
    logger.info("Purging cache")

    resp = requests.post(fastly_url, headers=headers)
    resp.raise_for_status()
