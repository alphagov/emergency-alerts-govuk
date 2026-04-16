# Building upon the basic logging config in utils, add a filter that takes relevant data from
# the Celery publish task so that all log lines contain context/IDs for the task.

import logging

from emergency_alerts_utils import logging as utils_logging
from flask import Flask, g, has_app_context

FLASK_G_TASK_ID = "celery_task_id"
FLASK_G_BROADCAST_EVENT_ID = "broadcast_event_id"


class TaskLogFilter(logging.Filter):
    def filter(self, record):
        if has_app_context():
            task_name = g.get(FLASK_G_TASK_ID)
            if task_name is not None:
                setattr(record, FLASK_G_TASK_ID, task_name)

            broadcast_event_id = g.get(FLASK_G_BROADCAST_EVENT_ID)
            if broadcast_event_id is not None:
                setattr(record, FLASK_G_BROADCAST_EVENT_ID, broadcast_event_id)

        return True


def init_app(app: Flask):
    utils_logging.init_app(app)

    # Add to the handler instead of app.logger so that other loggers (libraries) inherit
    # the filter. (Calling .addFilter on the root logger won't propagate)
    for handler in logging.getLogger().handlers:
        handler.addFilter(TaskLogFilter())
