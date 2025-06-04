import os

# from flask import current_app
from kombu import Exchange, Queue


class Config():
    GOVUK_ALERTS_HOST_URL = os.environ.get("GOVUK_ALERTS_HOST_URL", "")

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

    QUEUE_NAME = "govuk-alerts"

    CELERY = {
        "broker_url": "filesystem://",
        "broker_transport_options": {
            "data_folder_in": "/tmp/.data/broker",
            "data_folder_out": "/tmp/.data/broker/",
        },
        "timezone": "Europe/London",
        "imports": ["app.celery.tasks"],
        "task_queues": [Queue(QUEUE_NAME, Exchange("default"), routing_key=QUEUE_NAME)],
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

    PREDEFINED_SQS_QUEUES = {
        QUEUE_NAME: {
            "url": f"{SQS_QUEUE_BASE_URL}/{QUEUE_PREFIX}{QUEUE_NAME}"
        }
    }

    CELERY = {
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": AWS_REGION,
            "predefined_queues": PREDEFINED_SQS_QUEUES,
            "is_secure": True,
            "task_acks_late": True,
        },
        "timezone": "UTC",
        "imports": ["app.celery.tasks"],
        "task_queues": [Queue(QUEUE_NAME, Exchange("default"), routing_key=QUEUE_NAME)],
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
