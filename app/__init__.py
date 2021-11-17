import os

from flask import Flask
from notifications_utils import logging
from notifications_utils.celery import NotifyCelery
from notifications_utils.clients.statsd.statsd_client import StatsdClient

from app.notify_client.alerts_api_client import AlertsApiClient
from app.utils import DIST

notify_celery = NotifyCelery()
statsd_client = StatsdClient()
alerts_api_client = AlertsApiClient()


def create_app():
    application = Flask(
        __name__,
        static_folder=str(DIST),
    )

    from app.config import configs
    environment = os.getenv('NOTIFY_ENVIRONMENT', 'development')
    application.config.from_object(configs[environment])

    from app.main import bp as main
    application.register_blueprint(main)

    from app.commands import setup_commands
    setup_commands(application)

    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)
    notify_celery.init_app(application)
    alerts_api_client.init_app(application)

    return application
