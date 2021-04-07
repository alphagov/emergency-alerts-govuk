import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
)
from notifications_utils.formatters import formatted_list

repo = Path('.')
src = repo / 'src'
dist = repo / 'dist'
root = dist / 'alerts'
now = datetime.now(timezone.utc)


jinja_loader = ChoiceLoader([
    FileSystemLoader(str(repo)),
    PrefixLoader({
        'govuk_frontend_jinja': PackageLoader('govuk_frontend_jinja')
    })
])


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


def file_fingerprint(path):
    contents = open(str(dist) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()


def is_current_alert(alert):
    if alert['message_type'] == 'cancel':
        return False
    if alert['expires'] <= now:  # pyyaml converts ISO 8601 dates to datetime.datetime instances
        return False
    return True


def convert_dates(alert):
    alert['sent'] = AlertsDate(alert['sent'])
    alert['expires'] = AlertsDate(alert['expires'])
    return alert


data_file = repo / 'data.yaml'
with data_file.open() as stream:
    data = yaml.load(stream, Loader=yaml.CLoader)

env = Environment(loader=jinja_loader, autoescape=True)
env.filters['file_fingerprint'] = file_fingerprint
env.filters['formatted_list'] = formatted_list
env.globals = {
    'font_paths': [
        item.relative_to(dist)
        for item in root.glob('assets/fonts/*.woff2')
    ],
    'data_last_updated': AlertsDate(data['last_updated']),
    'current_alerts': [convert_dates(alert) for alert in data['alerts'] if is_current_alert(alert)]
}

if __name__ == '__main__':
    root.mkdir(exist_ok=True)

    for page in src.glob('*.html'):
        template = env.get_template(str(page))

        if 'alert.html' in str(page):
            for alert in data['alerts']:
                target = root / alert['identifier']
                target.open('w').write(template.render({'alert_data': alert}))
            continue

        if 'index.html' in str(page):
            target = dist / page.relative_to(src)
        else:
            target = root / page.relative_to(src)

        target.parent.mkdir(exist_ok=True)
        target.open('w').write(template.render())
        if 'index.html' not in str(page):
            target.replace(str(target).replace(".html", ""))
