import hashlib
from pathlib import Path

REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


def file_fingerprint(path, root=DIST):
    contents = open(str(root) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()
