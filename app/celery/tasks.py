import time

from emergency_alerts_utils.celery import TaskNames
from flask import current_app

from app import notify_celery
from app.models.alerts import Alerts
from app.notify_client.alerts_api_client import alerts_api_client
from app.render import get_cap_xml_for_alerts, get_rendered_pages
from app.utils import (
    delete_timestamp_file_from_s3,
    post_version_to_cloudwatch,
    purge_fastly_cache,
    put_success_metric_data,
    upload_cap_xml_to_s3,
    upload_html_to_s3,
)


@notify_celery.task(
    bind=True,
    name=TaskNames.PUBLISH_GOVUK_ALERTS,
    max_retries=20,
    retry_backoff=True,
    retry_backoff_max=300,
)
def publish_govuk_alerts(self, broadcast_event_id=""):
    try:
        task_id = self.request.id
        alerts = Alerts.load()
        rendered_pages = get_rendered_pages(alerts)
        cap_xml_alerts = get_cap_xml_for_alerts(alerts)

        if not current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]:
            current_app.logger.info("Skipping upload to S3 in local environment")
            return

        upload_html_to_s3(rendered_pages, task_id, broadcast_event_id)
        upload_cap_xml_to_s3(cap_xml_alerts, task_id, broadcast_event_id)
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
        delete_timestamp_file_from_s3(task_id)
        put_success_metric_data("publish-dynamic")
    except Exception:
        current_app.logger.exception("Failed to publish content to gov.uk/alerts")
        self.retry(queue=current_app.config['QUEUE_NAME'])


@notify_celery.task(name=TaskNames.TRIGGER_GOVUK_HEALTHCHECK)
def trigger_govuk_alerts_healthcheck():
    try:
        post_version_to_cloudwatch()

        time_stamp = int(time.time())
        with open("/eas/emergency-alerts-govuk/celery-beat-healthcheck", mode="w") as file:
            file.write(str(time_stamp))
        current_app.logger.debug(f"file.write successful - govuk-alerts health check timestamp: {time_stamp}")
    except Exception:
        current_app.logger.exception("Unable to generate health-check timestamp")
        raise
