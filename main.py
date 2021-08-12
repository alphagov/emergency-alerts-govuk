import os

from flask import Flask

from app import create_app, notify_celery  # noqa
from app.render import alerts_from_yaml, get_rendered_pages

application = Flask(
    'notify-govuk-alerts',
    static_folder='dist/',
)


@application.route('/<path:key>', methods=['GET'])
def show_page(key):
    if os.getenv("FLASK_ENV") != "development":
        return "not found", 404

    alerts = alerts_from_yaml()
    rendered_pages = get_rendered_pages(alerts)

    if key in rendered_pages:
        return rendered_pages[key]

    return application.send_static_file(key)


create_app(application)
application.app_context().push()
