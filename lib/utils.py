import hashlib
import pytz
from datetime import datetime
from pathlib import Path
from lib.alert_date import AlertDate


REPO = Path('.')
SRC = REPO / 'src'
DIST = REPO / 'dist'
ROOT = DIST / 'alerts'


def file_fingerprint(path, root=DIST):
    contents = open(str(root) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()


def is_current_alert(alert):
    now = datetime.now(pytz.utc)

    if alert['expires'].astimezone(pytz.utc) <= now:  # pyyaml converts ISO 8601 dates to datetime.datetime instances
        return False
    return True


def convert_dates(alert):
    alert['sent'] = AlertDate(alert['sent'])
    alert['expires'] = AlertDate(alert['expires'])
    return alert
