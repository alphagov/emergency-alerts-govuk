from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
)
from notifications_utils.formatters import formatted_list

from app.utils import DIST, REPO, file_fingerprint, paragraphize

TEMPLATES = REPO / 'app' / 'templates'
VIEWS = REPO / 'src'

all_view_paths = [
    str(path.relative_to(VIEWS)) for path in VIEWS.glob('*.html')
]


def setup_jinja_environment(alerts):
    jinja_loader = ChoiceLoader([
        FileSystemLoader(str(TEMPLATES)),
        FileSystemLoader(str(VIEWS)),
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
            for item in DIST.glob('alerts/assets/fonts/*.woff2')
        ],
        'alerts': alerts,
    }

    return env


def get_rendered_pages(alerts):
    env = setup_jinja_environment(alerts)
    rendered = {}

    for path in all_view_paths:
        template = env.get_template(path)
        target = path.replace(".html", "")

        # render each individual alert's page
        if target == 'alert':
            for alert in alerts.public:
                rendered["alerts/" + alert.identifier] = template.render({'alert_data': alert})
            continue

        if target == 'index':
            rendered['alerts'] = template.render()
            continue

        rendered["alerts/" + target] = template.render()

    return rendered
