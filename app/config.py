import os

from kombu import Exchange, Queue


class Config():
    GOVUK_ALERTS_HOST_URL = os.environ.get("GOVUK_ALERTS_HOST_URL", "")

    QUEUE_PREFIX = os.getenv("NOTIFICATION_QUEUE_PREFIX")
    QUEUE_NAME = "govuk-alerts"

    EAS_APP_NAME = "govuk-alerts"

    BROADCASTS_AWS_ACCESS_KEY_ID = os.getenv("BROADCASTS_AWS_ACCESS_KEY_ID")
    BROADCASTS_AWS_SECRET_ACCESS_KEY = os.getenv("BROADCASTS_AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")
    GOVUK_ALERTS_S3_BUCKET_NAME = os.getenv("GOVUK_ALERTS_S3_BUCKET_NAME")

    FASTLY_SERVICE_ID = os.getenv("FASTLY_SERVICE_ID")
    FASTLY_API_KEY = os.getenv("FASTLY_API_KEY")
    FASTLY_SURROGATE_KEY = "notify-emergency-alerts"

    NOTIFY_API_HOST_NAME = os.environ.get("API_HOST_NAME", "http://localhost:6011")
    NOTIFY_API_CLIENT_SECRET = "govuk-alerts-secret-key"
    NOTIFY_API_CLIENT_ID = "govuk-alerts"

    CELERY = {
        # "broker":"sqs://",
        "broker_url": f"https://sqs.{AWS_REGION}.amazonaws.com",
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": AWS_REGION,
            "queue_name_prefix": QUEUE_PREFIX,
            # "predefined_queues": {
            #     QUEUE_NAME: {
            #         "url": f"https://sqs.{AWS_REGION}.amazonaws.com/{QUEUE_PREFIX}-{QUEUE_NAME}",
            #     }
            # },
            # "wait_time_seconds": 20,  # enable long polling, with a wait time of 20 seconds
        },
        "timezone": "UTC",
        "imports": ["app.celery.tasks"],
        "task_queues": [Queue(QUEUE_NAME, Exchange("default"), routing_key=QUEUE_NAME)],
        # Restart workers after a few tasks have been executed - this will help prevent any memory leaks
        # (not that we should be encouraging sloppy memory management). Although the tasks are time-critical,
        # we don't expect to get them in quick succession, so a small restart delay is acceptable.
        "worker_max_tasks_per_child": 10
    }

    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests.yaml"


class Hosted(Config):
    # Prefix to identify queues in SQS
    TENANT = f"{os.environ.get('TENANT')}." if os.environ.get("TENANT") is not None else ""
    TENANT_PREFIX = f"{os.environ.get('TENANT')}-" if os.environ.get("TENANT") is not None else ""
    ENVIRONMENT = os.getenv('ENVIRONMENT')
    ENVIRONMENT_PREFIX = ENVIRONMENT if ENVIRONMENT != 'development' else 'dev'

    QUEUE_PREFIX = f"{ENVIRONMENT_PREFIX}-{TENANT_PREFIX}"
    SQS_QUEUE_BASE_URL = os.getenv("SQS_QUEUE_BASE_URL")
    QUEUE_NAME = "govuk-alerts"
    SQS_QUEUE_BACKOFF_POLICY = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16, 6: 32, 7: 64, 8: 128}

    EAS_APP_NAME = "govuk-alerts"

    BROADCASTS_AWS_ACCESS_KEY_ID = os.getenv("BROADCASTS_AWS_ACCESS_KEY_ID")
    BROADCASTS_AWS_SECRET_ACCESS_KEY = os.getenv("BROADCASTS_AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")
    GOVUK_ALERTS_S3_BUCKET_NAME = os.getenv("GOVUK_ALERTS_S3_BUCKET_NAME")

    FASTLY_SERVICE_ID = os.getenv("FASTLY_SERVICE_ID")
    FASTLY_API_KEY = os.getenv("FASTLY_API_KEY")
    FASTLY_SURROGATE_KEY = "notify-emergency-alerts"

    NOTIFY_API_HOST_NAME = f"http://api.{TENANT}ecs.local:6011"
    NOTIFY_API_CLIENT_SECRET = os.environ.get("NOTIFY_API_CLIENT_SECRET")
    NOTIFY_API_CLIENT_ID = "govuk-alerts"

    CELERY = {
        # "broker":"sqs://",
        "broker_url": f"https://sqs.{AWS_REGION}.amazonaws.com",
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": AWS_REGION,
            "queue_name_prefix": QUEUE_PREFIX,
            # "predefined_queues": {
            #     QUEUE_NAME: {
            #         "url": f"{SQS_QUEUE_BASE_URL}/{QUEUE_PREFIX}{QUEUE_NAME}",
            #         "backoff_policy": SQS_QUEUE_BACKOFF_POLICY
            #     },
            # },
        },
        "timezone": "UTC",
        "imports": ["app.celery.tasks"],
        "task_queues": [Queue(QUEUE_NAME, Exchange("default"), routing_key=QUEUE_NAME)],
        "worker_log_format": "[%(levelname)s] %(message)s",
        # Restart workers after a few tasks have been executed - this will help prevent any memory leaks
        # (not that we should be encouraging sloppy memory management). Although the tasks are time-critical,
        # we don't expect to get them in quick succession, so a small restart delay is acceptable.
        "worker_max_tasks_per_child": 10
    }

    PLANNED_TESTS_YAML_FILE_NAME = "planned-tests.yaml"


class Test(Config):
    DEBUG = True
    GOVUK_ALERTS_HOST_URL = os.environ.get("GOVUK_ALERTS_HOST_URL", "http://localhost:6017")

    FASTLY_SERVICE_ID = "test-service-id"
    FASTLY_API_KEY = "test-api-key"
    FASTLY_SURROGATE_KEY = "test-surrogate-key"

    BROADCASTS_AWS_ACCESS_KEY_ID = "test-key-id"
    BROADCASTS_AWS_SECRET_ACCESS_KEY = "test-secret-key"
    GOVUK_ALERTS_S3_BUCKET_NAME = "test-bucket-name"


configs = {
    "local": Config,
    "hosted": Hosted,
    "test": Test,
}
