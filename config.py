import os

from kombu import Exchange, Queue

class Config():
    NOTIFICATION_QUEUE_PREFIX = os.getenv('NOTIFICATION_QUEUE_PREFIX')

    # Logging
    DEBUG = False
    LOGGING_STDOUT_JSON = os.getenv('LOGGING_STDOUT_JSON') == '1'

    NOTIFY_APP_NAME = 'govuk-alerts-publisher'
    AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
    NOTIFY_LOG_PATH = os.getenv('NOTIFY_LOG_PATH', '/var/log/notify/application.log')

    CELERY = {
        'broker_url': 'sqs://',
        'broker_transport_options': {
            'region': AWS_REGION,
            'visibility_timeout': 310,
            'queue_name_prefix': NOTIFICATION_QUEUE_PREFIX,
            'wait_time_seconds': 20,  # enable long polling, with a wait time of 20 seconds
        },
        'timezone': 'Europe/London',
        'imports': ['celery.tasks'],
        'task_queues': [
            Queue('publish-govuk-alerts', Exchange('default'), routing_key='publish-govuk-alerts')
        ],
        # restart workers after each task is executed - this will help prevent any memory leaks (not that we should be
        # encouraging sloppy memory management). Since we only run a handful of tasks per day, and none are time
        # sensitive, the extra couple of seconds overhead isn't seen to be a huge issue.
        'worker_max_tasks_per_child': 20
    }

    STATSD_HOST = os.getenv('STATSD_HOST')
    STATSD_PORT = 8125
    STATSD_ENABLED = bool(STATSD_HOST)
