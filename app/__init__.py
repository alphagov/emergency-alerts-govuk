import os

import opentelemetry.instrumentation.auto_instrumentation.sitecustomize  # noqa
from emergency_alerts_utils.dramatiq import EasSqsFlaskDramatiq
from emergency_alerts_utils.dramatiq.instrumentation import DramatiqInstrumentor
from flask import Flask

from app import govuk_logging
from app.notify_client.alerts_api_client import (
    alerts_api_client,
    publish_api_client,
)
from app.utils import DIST

DramatiqInstrumentor().instrument()

dramatiq_instance = EasSqsFlaskDramatiq()


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

    govuk_logging.init_app(application)
    dramatiq_instance.init_app(application, application.config["QUEUE_PREFIX"])
    alerts_api_client.init_app(application)
    publish_api_client.init_app(application)

    return application
