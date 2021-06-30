import os
import re
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
    path = Path(path).relative_to('/')  # path comes in as absolute, rooted to the dist folder
    path_regex = re.compile(f'^{path.stem}-[0-9a-z]{{8}}{path.suffix}$')  # regexp based on the filename + a 8 char hash
    matches = [
                filename for filename
                in os.listdir(str(root / path.parent))
                if path_regex.search(filename)]

    if len(matches) == 0:
        raise OSError(f'{str(root / path.parent / path.stem)}-[hash]{path.suffix} referenced but not available')

    return f'/{path.parent}/{matches[0]}'
