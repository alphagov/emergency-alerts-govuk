import os
import sys
import traceback

import gunicorn
from gds_metrics.gunicorn import child_exit  # noqa

workers = 5
errorlog = "/home/vcap/logs/gunicorn_error.log"
bind = "0.0.0.0:{}".format(os.getenv("PORT"))
disable_redirect_access_to_syslog = True
gunicorn.SERVER_SOFTWARE = 'None'


def worker_abort(worker):
    worker.log.info("worker received ABORT")
    for stack in sys._current_frames().values():
        worker.log.error(''.join(traceback.format_stack(stack)))
