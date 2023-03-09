import click

# from app.celery.tasks import publish_govuk_alerts
from flask import current_app
from flask import cli

from app.models.alerts import Alerts
from app.render import get_rendered_pages
from app.utils import purge_fastly_cache, upload_to_s3


def setup_commands(app):
    app.cli.add_command(publish)


@click.command('publish')
@cli.with_appcontext
def publish():
    # publish_govuk_alerts()
    try:
        alerts = Alerts.load()
        rendered_pages = get_rendered_pages(alerts)

        upload_to_s3(rendered_pages)
        purge_fastly_cache()
    except Exception:
        current_app.logger.exception("Failed to publish content to gov.uk/alerts")
