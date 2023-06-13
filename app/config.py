import os

from kombu import Exchange, Queue


class Config():
    NOTIFICATION_QUEUE_PREFIX = os.getenv("NOTIFICATION_QUEUE_PREFIX")
    QUEUE_NAME = "govuk-alerts"

    NOTIFY_APP_NAME = "govuk-alerts"
    NOTIFY_LOG_PATH = os.getenv("NOTIFY_LOG_PATH", "application.log")

    BROADCASTS_AWS_ACCESS_KEY_ID = os.getenv("BROADCASTS_AWS_ACCESS_KEY_ID")
    BROADCASTS_AWS_SECRET_ACCESS_KEY = os.getenv("BROADCASTS_AWS_SECRET_ACCESS_KEY")
    BROADCASTS_AWS_REGION = "eu-west-2"
    GOVUK_ALERTS_S3_BUCKET_NAME = os.getenv("GOVUK_ALERTS_S3_BUCKET_NAME")

    FASTLY_SERVICE_ID = os.getenv("FASTLY_SERVICE_ID")
    FASTLY_API_KEY = os.getenv("FASTLY_API_KEY")
    FASTLY_SURROGATE_KEY = "notify-emergency-alerts"

    NOTIFY_API_HOST_NAME = os.environ.get("NOTIFY_API_HOST_NAME")
    NOTIFY_API_CLIENT_SECRET = os.environ.get("NOTIFY_API_CLIENT_SECRET")
    NOTIFY_API_CLIENT_ID = "govuk-alerts"

    CELERY = {
        "broker_url": "sqs://",
        "broker_transport_options": {
            "region": "eu-west-1",
            "visibility_timeout": 310,
            "queue_name_prefix": NOTIFICATION_QUEUE_PREFIX,
            "wait_time_seconds": 20,  # enable long polling, with a wait time of 20 seconds
        },
        "timezone": "Europe/London",
        "imports": ["app.celery.tasks"],
        "task_queues": [
            Queue(QUEUE_NAME, Exchange("default"), routing_key=QUEUE_NAME)
        ],
        # Restart workers after a few tasks have been executed - this will help prevent any memory leaks
        # (not that we should be encouraging sloppy memory management). Although the tasks are time-critical,
        # we don't expect to get them in quick succession, so a small restart delay is acceptable.
        "worker_max_tasks_per_child": 20
    }

    STATSD_HOST = os.getenv("STATSD_HOST")
    STATSD_PORT = 8125
    STATSD_ENABLED = bool(STATSD_HOST)

    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests.yaml"


class Decoupled(Config):
    # Prefix to identify queues in SQS
    NOTIFICATION_QUEUE_PREFIX = f"{os.getenv('ENVIRONMENT')}-"
    SQS_QUEUE_BASE_URL = os.getenv("SQS_QUEUE_BASE_URL")
    QUEUE_NAME = "govuk-alerts"
    SQS_QUEUE_BACKOFF_POLICY = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16, 6: 32, 7: 64, 8: 128}

    NOTIFY_APP_NAME = "govuk-alerts"
    NOTIFY_LOG_PATH = os.getenv("NOTIFY_LOG_PATH", "application.log")

    BROADCASTS_AWS_ACCESS_KEY_ID = os.getenv("BROADCASTS_AWS_ACCESS_KEY_ID")
    BROADCASTS_AWS_SECRET_ACCESS_KEY = os.getenv("BROADCASTS_AWS_SECRET_ACCESS_KEY")
    BROADCASTS_AWS_REGION = "eu-west-2"
    GOVUK_ALERTS_S3_BUCKET_NAME = os.getenv("GOVUK_ALERTS_S3_BUCKET_NAME")

    FASTLY_SERVICE_ID = os.getenv("FASTLY_SERVICE_ID")
    FASTLY_API_KEY = os.getenv("FASTLY_API_KEY")
    FASTLY_SURROGATE_KEY = "notify-emergency-alerts"

    NOTIFY_API_HOST_NAME = "http://api.ecs.local:6011"
    NOTIFY_API_CLIENT_SECRET = os.environ.get("NOTIFY_API_CLIENT_SECRET")
    NOTIFY_API_CLIENT_ID = "govuk-alerts"

    CELERY = {
        "broker_url": "sqs://",
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": "eu-west-2",
            "predefined_queues": {
                QUEUE_NAME: {
                    "url": f"{SQS_QUEUE_BASE_URL}/{NOTIFICATION_QUEUE_PREFIX}govuk-alerts",
                    "backoff_policy": SQS_QUEUE_BACKOFF_POLICY
                }
            }
        },
        "timezone": "UTC",
        "imports": ["app.celery.tasks"],
        "task_queues": [
            Queue(QUEUE_NAME, Exchange("default"), routing_key=QUEUE_NAME)
        ],
        "worker_log_format": "[%(levelname)s] %(message)s",
        # Restart workers after a few tasks have been executed - this will help prevent any memory leaks
        # (not that we should be encouraging sloppy memory management). Although the tasks are time-critical,
        # we don't expect to get them in quick succession, so a small restart delay is acceptable.
        "worker_max_tasks_per_child": 10
    }

    STATSD_HOST = os.getenv("STATSD_HOST")
    STATSD_PORT = 8125
    STATSD_ENABLED = bool(STATSD_HOST)

    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests.yaml"


class Development(Config):
    NOTIFY_API_CLIENT_SECRET = "govuk-alerts-secret-key"
    NOTIFY_API_HOST_NAME = "http://localhost:6011"

    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests-dev.yaml"


class Test(Config):
    DEBUG = True

    FASTLY_SERVICE_ID = "test-service-id"
    FASTLY_API_KEY = "test-api-key"
    FASTLY_SURROGATE_KEY = "test-surrogate-key"

    BROADCASTS_AWS_ACCESS_KEY_ID = "test-key-id"
    BROADCASTS_AWS_SECRET_ACCESS_KEY = "test-secret-key"
    GOVUK_ALERTS_S3_BUCKET_NAME = "test-bucket-name"


class Staging(Config):
    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests-staging.yaml"


class Preview(Config):
    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests-preview.yaml"


configs = {
    "development": Development,
    "decoupled": Decoupled,
    "test": Test,
    "staging": Staging,
    "preview": Preview,
    "production": Config,
}
