import time

from emergency_alerts_utils.tasks import QueueNames, TaskNames
from flask import current_app, g
from opentelemetry import trace

from app import dramatiq_instance
from app.govuk_logging import FLASK_G_BROADCAST_EVENT_ID
from app.models.alerts import Alerts
from app.models.publish_task_progress import PublishTaskProgress
from app.notify_client.alerts_api_client import alerts_api_client
from app.render import get_cap_xml_for_alerts, get_rendered_pages
from app.utils import (
    archive_website,
    post_version_to_cloudwatch,
    purge_fastly_cache,
    setup_s3_session,
    upload_cap_xml_to_s3,
    upload_html_to_s3,
)

tracer = trace.get_tracer(__name__)


@dramatiq_instance.actor(
    actor_name=TaskNames.PUBLISH_GOVUK_ALERTS,
    queue_name=QueueNames.GOVUK_ALERTS,
    allow_retry=True,
)
def publish_govuk_alerts(broadcast_event_id=""):
    setattr(g, FLASK_G_BROADCAST_EVENT_ID, broadcast_event_id)

    try:
        current_app.logger.info(
            "Starting GovUK publish. (Triggered by broadcast event: %s)",
            broadcast_event_id,
        )

        current_app.logger.info("Loading alerts")
        publish_task_progress = PublishTaskProgress.create(
            publish_type="publish-dynamic", publish_origin="dramatiq"
        )
        with tracer.start_as_current_span("Get live alerts"):
            alerts = Alerts.load(publish_task_progress)
            current_app.logger.info("Alerts loaded")

        cut_off = _get_govuk_archive_timestamp()

        with tracer.start_as_current_span("Render pages"):
            rendered_pages = get_rendered_pages(alerts, cut_off=cut_off, publish_task_progress=publish_task_progress)
            current_app.logger.info("Pages rendered")

        with tracer.start_as_current_span("Render CAP XML"):
            cap_xml_alerts = get_cap_xml_for_alerts(alerts, publish_task_progress)
            current_app.logger.info("CAP XML rendered")

        if not current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]:
            current_app.logger.info("Skipping upload to S3 in local environment")
            return

        with tracer.start_as_current_span("Upload HTML to S3"):
            current_app.logger.info("Uploading %d files to S3", len(rendered_pages))
            upload_html_to_s3(rendered_pages, publish_task_progress)

        with tracer.start_as_current_span("Upload CAP to S3"):
            current_app.logger.info("Uploading %d files to S3", len(cap_xml_alerts))
            upload_cap_xml_to_s3(cap_xml_alerts, publish_task_progress)

        current_app.logger.info("Finished uploading to S3. Purging Fastly.")
        purge_fastly_cache()
        current_app.logger.info("Fastly purged. Acknowledging to API.")
        alerts_api_client.send_publish_acknowledgement()
        publish_task_progress.set_to_finished()

        with tracer.start_as_current_span("Archive website to S3"):
            archive_website(html=rendered_pages, capxml=cap_xml_alerts, assets=None)
            current_app.logger.info("Website archived")

        current_app.logger.info("Finished GovUK publish")
    except Exception as e:
        current_app.logger.exception("Failed to publish content to gov.uk/alerts")
        raise e


@dramatiq_instance.actor(
    actor_name=TaskNames.TRIGGER_GOVUK_HEALTHCHECK, queue_name=QueueNames.GOVUK_ALERTS
)
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


def _get_govuk_archive_timestamp():
    bucket = current_app.config["GOVUK_ALERTS_ARCHIVE_S3_BUCKET_NAME"]
    if not bucket:
        current_app.logger.info("Skipping retrieval of archive timestamp in local environment")
        return None

    try:
        s3 = setup_s3_session()
        response = s3.head_object(Bucket=bucket, Key="archive_govuk-alerts-website.tar.gz")
        timestamp = response["LastModified"]
        current_app.logger.info(f"Retrieved archive timestamp: {timestamp}")
        return timestamp
    except Exception:
        current_app.logger.exception("Unable to retrieve archive timestamp")
        return None
