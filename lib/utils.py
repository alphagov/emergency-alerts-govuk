import hashlib
import pytz
from datetime import datetime
from pathlib import Path


REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


def file_fingerprint(path, root=DIST):
    contents = open(str(root) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()


def is_current_alert(alert):
    now = datetime.now(pytz.utc)

    if alert.expires.as_utc_datetime <= now:
        return False
    return True
