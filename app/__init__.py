import os

from flask import Flask
from notifications_utils import logging
from notifications_utils.clients.statsd.statsd_client import StatsdClient

from app.celery.celery import NotifyCelery
from app.render import alerts_from_yaml, get_rendered_pages

notify_celery = NotifyCelery()
statsd_client = StatsdClient()


def create_app():
    application = Flask(
        __name__,
        static_folder='../dist/',
    )

    from app.config import configs
    environment = os.getenv('NOTIFY_ENVIRONMENT', 'development')
    application.config.from_object(configs[environment])

    from app.commands import setup_commands
    setup_commands(application)

    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)
    notify_celery.init_app(application)

    @application.route('/<path:key>', methods=['GET'])
    def show_page(key):
        alerts = alerts_from_yaml()
        rendered_pages = get_rendered_pages(alerts)

        if key in rendered_pages:
            return rendered_pages[key]

        return application.send_static_file(key)

    return application
