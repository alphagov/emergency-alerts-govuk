import hashlib
import pytz
from datetime import datetime
from pathlib import Path
from pytz import timezone


REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


class AlertsDate(object):
    """Makes a datetime available in different formats"""

    def __init__(self, _datetime):
        self._datetime = _datetime
        self._local_datetime = _datetime.astimezone(timezone('Europe/London'))

    @property
    def as_lang(self, lang='en-GB'):
        return '{dt.day} {dt:%B} {dt:%Y} at {dt:%H}:{dt:%M}'.format(dt=self._local_datetime)

    @property
    def as_iso8601(self):
        return self._local_datetime.isoformat()

    @property
    def as_datetime(self):
        return self._datetime

    @property
    def as_local_datetime(self):
        return self._local_datetime


def file_fingerprint(path, root=DIST):
    contents = open(str(root) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()


def is_current_alert(alert):
    now = datetime.now(pytz.utc)

    if alert['message_type'] == 'cancel':
        return False
    if alert['expires'].astimezone(pytz.utc) <= now:  # pyyaml converts ISO 8601 dates to datetime.datetime instances
        return False
    return True


def convert_dates(alert):
    alert['sent'] = AlertsDate(alert['sent'])
    alert['expires'] = AlertsDate(alert['expires'])
    return alert
