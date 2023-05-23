import time

from flask import current_app

from app import notify_celery
from app.models.alerts import Alerts
from app.render import get_rendered_pages
from app.utils import purge_fastly_cache, upload_html_to_s3


@notify_celery.task(bind=True, name="publish-govuk-alerts", max_retries=20, retry_backoff=True, retry_backoff_max=300)
def publish_govuk_alerts(self):
    try:
        alerts = Alerts.load()
        rendered_pages = get_rendered_pages(alerts)

        upload_html_to_s3(rendered_pages)
        purge_fastly_cache()
    except Exception:
        current_app.logger.exception("Failed to publish content to gov.uk/alerts")
        self.retry(queue=current_app.config['QUEUE_NAME'])


@notify_celery.task(name="trigger-govuk-alerts-healthcheck")
def trigger_govuk_alerts_healthcheck(self):
    try:
        time_stamp = int(time.time())
        with open("/eas/emergency-alerts-govuk/celery-beat-healthcheck", mode="w") as file:
            file.write(str(time_stamp))
    except Exception:
        current_app.logger.exception("Unable to generate health-check timestamp")
        raise
