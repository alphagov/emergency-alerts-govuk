import logging

from opentelemetry.instrumentation.auto_instrumentation import initialize

initialize()

from app import create_app, notify_celery  # noqa

application = create_app()
application.app_context().push()

logger = logging.getLogger(__name__)
logger.info("run_celery init")
