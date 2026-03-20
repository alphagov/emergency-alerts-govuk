import click
from flask import cli, current_app

from app.models.alerts import Alerts
from app.models.publish_task_progress import PublishTaskProgress
from app.notify_client.alerts_api_client import alerts_api_client
from app.render import get_cap_xml_for_alerts, get_rendered_pages
from app.utils import (
    purge_fastly_cache,
    upload_assets_to_s3,
    upload_cap_xml_to_s3,
    upload_html_to_s3,
)


def setup_commands(app):
    app.cli.add_command(publish)
    app.cli.add_command(publish_with_assets)


@click.command('publish')
@cli.with_appcontext
def publish():
    try:
        publish_task_progress = PublishTaskProgress.create(publish_type="publish-dynamic", publish_origin="cli")
        _publish_html(publish_task_progress)
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
        publish_task_progress.set_to_finished()
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


@click.command('publish-with-assets')
@click.option("--startup", is_flag=True)
@cli.with_appcontext
def publish_with_assets(startup):
    try:
        origin = "startup" if startup else "cli"
        publish_task_progress = PublishTaskProgress.create(publish_type="publish-all", publish_origin=origin)
        _publish_html(publish_task_progress)
        _publish_cap_xml(publish_task_progress)
        _publish_assets(publish_task_progress)
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
        publish_task_progress.set_to_finished()
    except FileExistsError as e:
        current_app.logger.exception(f"Publish assets FAILED: {e}")
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


def _publish_html(publish_task_progress):
    current_app.logger.info("Starting load of alerts")
    alerts = Alerts.load(publish_task_progress)
    current_app.logger.info("Starting render of pages")
    rendered_pages = get_rendered_pages(alerts, publish_task_progress)
    current_app.logger.info("Ending render of pages")
    upload_html_to_s3(rendered_pages, publish_task_progress)


def _publish_assets(publish_task_progress):
    upload_assets_to_s3(publish_task_progress)


def _publish_cap_xml(publish_task_progress):
    alerts = Alerts.load(
        publish_task_progress
    )
    cap_xml_alerts = get_cap_xml_for_alerts(alerts, publish_task_progress)
    upload_cap_xml_to_s3(
        cap_xml_alerts,
        publish_task_progress
    )
