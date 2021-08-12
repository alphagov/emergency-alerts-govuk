from notifications_utils import logging
from notifications_utils.clients.statsd.statsd_client import StatsdClient

from app.celery.celery import NotifyCelery

notify_celery = NotifyCelery()
statsd_client = StatsdClient()


def create_app(application):
    from app import config
    application.config.from_object(config.Config)

    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)
    notify_celery.init_app(application)

    return application
