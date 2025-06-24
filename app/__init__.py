import os

from celery import signals
from emergency_alerts_utils import logging
from emergency_alerts_utils.celery import NotifyCelery
from flask import Flask, current_app

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


@signals.task_prerun.connect
def mark_task_active(*args, **kwargs):
    task = kwargs.get("task", None)
    if task is None:
        return
    try:
        current_app.logger.info(
            f"[celery task_prerun] {task.name}",
            extra={
                "task_id": kwargs["task_id"],
                "broadcast_event_id": kwargs["kwargs"].get("broadcast_event_id", None),
                "provider": kwargs["kwargs"].get("provider", None),
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error logging task_prerun: {e}")


@signals.task_postrun.connect
def clear_task_context(*args, **kwargs):
    task = kwargs.get("task", None)
    if task is None:
        return
    try:
        current_app.logger.info(
            f"[celery task_postrun] {task.name}",
            extra={
                "task_id": kwargs["task_id"],
                "retval": kwargs["retval"],
                "state": kwargs["state"],
                "broadcast_event_id": kwargs["kwargs"].get("broadcast_event_id", None),
                "provider": kwargs["kwargs"].get("provider", None),
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error logging task_postrun: {e}")
