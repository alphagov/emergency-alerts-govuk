import hashlib
from datetime import datetime, timezone
from pathlib import Path


REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


class AlertsDate(object):
    """Makes a datetime available in different formats"""

    def __init__(self, _datetime):
        self._datetime = _datetime

    @property
    def as_lang(self, lang='en-GB'):
        return '{dt.day} {dt:%B} {dt:%Y} at {dt:%H}:{dt:%M}'.format(dt=self._datetime)

    @property
    def as_iso8601(self):
        return self._datetime.isoformat()

    @property
    def as_datetime(self):
        return self._datetime


def file_fingerprint(path, root=DIST):
    contents = open(str(root) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()


def is_current_alert(alert):
    now = datetime.now(timezone.utc)  # TODO: test this works with British Summer Time (BST)

    if alert['message_type'] == 'cancel':
        return False
    if alert['expires'] <= now:  # pyyaml converts ISO 8601 dates to datetime.datetime instances
        return False
    return True
