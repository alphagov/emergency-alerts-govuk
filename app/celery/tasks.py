from flask import current_app

from app import notify_celery
from app.render import alerts_from_yaml, get_rendered_pages
from app.utils import purge_cache, upload_to_s3


@notify_celery.task(bind=True, name="publish-govuk-alerts", max_retries=20, retry_backoff=True, retry_backoff_max=300)
def publish_govuk_alerts(self):

    try:
        alerts = alerts_from_yaml()
        rendered_pages = get_rendered_pages(alerts)

        upload_to_s3(current_app.config, rendered_pages)

        purge_cache(current_app.config)
    except Exception:
        current_app.logger.exception("Failed to publish content to gov.uk/alerts: " + Exception)
        self.retry(queue=current_app.config['QUEUE_NAME'])
        return
