import click
from flask import cli, current_app

from app.models.alerts import Alerts
from app.models.publish_task_progress import PublishTaskProgress
from app.notify_client.alerts_api_client import alerts_api_client
from app.render import get_cap_xml_for_alerts, get_rendered_pages
from app.utils import (
    archive_website,
    get_publish_destination,
    prepare_destination,
    purge_fastly_cache,
    switch_destination,
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
        # get publish destination, based on currently configured blue/green configuration.
        # Throws exception of not blue or green - could mean break glass is in operation, or another publish
        # is in the process of swapping blue/green.
        publish_destination = get_publish_destination()

        # delete content from destination, except for assets
        prepare_destination(publish_destination, remove_assets=False)

        publish_task_progress = PublishTaskProgress.create(publish_type="publish-dynamic", publish_origin="cli")
        published_html = _publish_html(publish_task_progress)
        published_cap = _publish_cap_xml(publish_task_progress)
        purge_fastly_cache()
        switch_destination(publish_destination)
        alerts_api_client.send_publish_acknowledgement()
        publish_task_progress.set_to_finished()
        archive_website(html=published_html, capxml=published_cap)
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


@click.command('publish-with-assets')
@click.option("--startup", is_flag=True)
@cli.with_appcontext
def publish_with_assets(startup):
    try:
        origin = "startup" if startup else "cli"
        publish_task_progress = PublishTaskProgress.create(publish_type="publish-all", publish_origin=origin)
        published_html = _publish_html(publish_task_progress)
        published_cap = _publish_cap_xml(publish_task_progress)
        published_assets = _publish_assets(publish_task_progress)
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
        publish_task_progress.set_to_finished()
        archive_website(html=published_html, capxml=published_cap, assets=published_assets)
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
    return rendered_pages


def _publish_assets(publish_task_progress):
    assets = upload_assets_to_s3(publish_task_progress)
    return assets


def _publish_cap_xml(publish_task_progress):
    alerts = Alerts.load(
        publish_task_progress
    )
    cap_xml_alerts = get_cap_xml_for_alerts(alerts, publish_task_progress)
    upload_cap_xml_to_s3(
        cap_xml_alerts,
        publish_task_progress
    )
    return cap_xml_alerts
