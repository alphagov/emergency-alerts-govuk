import os

from flask import Flask

from notifications_utils import logging
from notifications_utils.clients.statsd.statsd_client import StatsdClient

import config
import notify_celery

notify_celery = notify_celery.NotifyCelery()
statsd_client = StatsdClient()


def create_app(application):
    application.config.from_object(config.Config)

    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)
    notify_celery.init_app(application)

    return application

@notify_celery.task(bind=True, name="publish-govuk-alerts", max_retries=5, default_retry_delay=300)
def publish_govuk_alerts(self):
    pass


application = Flask('notify-govuk-alerts-publisher')
create_app(application)
application.app_context().push()
