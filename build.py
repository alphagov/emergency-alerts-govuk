from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
)
from notifications_utils.formatters import formatted_list

from lib.alerts import Alerts
from lib.utils import DIST, REPO, ROOT, SRC, file_fingerprint, paragraphize


def setup_jinja_environment(alerts):
    jinja_loader = ChoiceLoader([
        FileSystemLoader(str(REPO)),
        PrefixLoader({
            'govuk_frontend_jinja': PackageLoader('govuk_frontend_jinja')
        })
    ])

    env = Environment(loader=jinja_loader, autoescape=True)
    env.filters['file_fingerprint'] = file_fingerprint
    env.filters['formatted_list'] = formatted_list
    env.filters['paragraphize'] = paragraphize
    env.globals = {
        'font_paths': [
            item.relative_to(DIST)
            for item in ROOT.glob('assets/fonts/*.woff2')
        ],
        'alerts': alerts,
    }

    return env


def alerts_from_yaml():
    alerts = Alerts.from_yaml(REPO / 'data.yaml')
    return alerts


def alerts_from_api():
    raise NotImplementedError("This has not been implemented yet")


def get_rendered_pages(alerts):
    env = setup_jinja_environment(alerts)

    rendered = {}
    for page in SRC.glob('*.html'):
        template = env.get_template(str(page))

        # render each individual alert's page
        if str(page) == 'src/alert.html':
            for alert in alerts.public:
                rendered["alerts/" + alert.identifier] = template.render({'alert_data': alert})
            continue

        if 'index.html' in str(page):
            rendered['alerts'] = template.render()
        else:
            target = str(page.relative_to(SRC))
            target = target.replace(".html", "")
            rendered["alerts/" + target] = template.render()

    return rendered
