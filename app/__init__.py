import os

from emergency_alerts_utils import logging
from emergency_alerts_utils.celery import NotifyCelery
from flask import Flask

from app.notify_client.alerts_api_client import AlertsApiClient
from app.utils import DIST

notify_celery = NotifyCelery()
alerts_api_client = AlertsApiClient()


def create_app():
    application = Flask(
        __name__,
        static_folder=str(DIST),
    )

    from app.config import configs
    environment = os.getenv('HOST', 'local')
    application.config.from_object(configs[environment])

    from app.main import bp as main
    application.register_blueprint(main)

    from app.commands import setup_commands
    setup_commands(application)

    logging.init_app(application)
    notify_celery.init_app(application)
    alerts_api_client.init_app(application)

    return application
