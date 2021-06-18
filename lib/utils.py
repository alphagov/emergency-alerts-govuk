import hashlib
import os
from pathlib import Path

from jinja2 import Markup, escape

REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


def paragraphize(value, classes="govuk-body-l govuk-!-margin-bottom-4"):
    paragraphs = [
        f'<p class="{classes}">{line}</p>'
        for line in escape(value).split('\n')
        if line
    ]
    return Markup('\n\n'.join(paragraphs))


def file_fingerprint(path, root=DIST):
    contents = open(str(root) + path, 'rb').read()
    hash = hashlib.md5(contents).hexdigest()
    filename, extension = os.path.splitext(path)
    return f'{filename}-{hash}{extension}'
