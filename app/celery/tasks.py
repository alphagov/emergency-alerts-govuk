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
