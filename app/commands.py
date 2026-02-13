import click
from flask import cli, current_app

from app.models.alerts import Alerts
from app.notify_client.alerts_api_client import alerts_api_client
from app.render import get_cap_xml_for_alerts, get_rendered_pages
from app.utils import (
    delete_timestamp_file_from_s3,
    purge_fastly_cache,
    put_success_metric_data,
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
        _publish_html()
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


@click.command('publish-with-assets')
@click.option('--container-id', default=None)
@click.option('--current-timestamp', default=None)
@cli.with_appcontext
def publish_with_assets(container_id, current_timestamp):
    try:
        publish_healthcheck_filename = f"{container_id}_{current_timestamp}"
        _publish_html(publish_healthcheck_filename)
        _publish_cap_xml(publish_healthcheck_filename)
        _publish_assets(publish_healthcheck_filename)
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
        delete_timestamp_file_from_s3(publish_healthcheck_filename)
        put_success_metric_data("publish-all")
    except FileExistsError as e:
        current_app.logger.exception(f"Publish assets FAILED: {e}")
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


def _publish_html(publish_healthcheck_filename):
    alerts = Alerts.load()
    rendered_pages = get_rendered_pages(alerts)
    upload_html_to_s3(rendered_pages, publish_healthcheck_filename)


def _publish_assets(publish_healthcheck_filename):
    upload_assets_to_s3(publish_healthcheck_filename)


def _publish_cap_xml(publish_healthcheck_filename):
    alerts = Alerts.load()
    cap_xml_alerts = get_cap_xml_for_alerts(alerts)
    upload_cap_xml_to_s3(cap_xml_alerts, publish_healthcheck_filename)
