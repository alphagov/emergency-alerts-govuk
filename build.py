from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
)
from notifications_utils.formatters import formatted_list

from lib.alerts import Alerts
from lib.utils import DIST, REPO, ROOT, SRC, file_fingerprint

jinja_loader = ChoiceLoader([
    FileSystemLoader(str(REPO)),
    PrefixLoader({
        'govuk_frontend_jinja': PackageLoader('govuk_frontend_jinja')
    })
])


alerts = Alerts.from_yaml(REPO / 'data.yaml')

env = Environment(loader=jinja_loader, autoescape=True)
env.filters['file_fingerprint'] = file_fingerprint
env.filters['formatted_list'] = formatted_list
env.globals = {
    'font_paths': [
        item.relative_to(DIST)
        for item in ROOT.glob('assets/fonts/*.woff2')
    ],
    'data_last_updated': alerts.last_updated_date,
    'current_alerts': alerts.current,
}

if __name__ == '__main__':
    ROOT.mkdir(exist_ok=True)

    for page in SRC.glob('*.html'):
        template = env.get_template(str(page))

        if str(page) == 'src/alert.html':
            for alert in alerts:
                target = ROOT / alert.identifier
                target.open('w').write(template.render({'alert_data': alert}))
            continue

        if 'index.html' in str(page):
            target = DIST / page.relative_to(SRC)
        else:
            target = ROOT / page.relative_to(SRC)

        target.parent.mkdir(exist_ok=True)
        target.open('w').write(template.render())
        if 'index.html' not in str(page):
            target.replace(str(target).replace(".html", ""))
