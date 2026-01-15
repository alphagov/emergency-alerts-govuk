import click
from flask import cli, current_app

from app.models.alerts import Alerts
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
        _publish_html()
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


@click.command('publish-with-assets')
@cli.with_appcontext
def publish_with_assets():
    try:
        _publish_html()
        _publish_cap_xml()
        _publish_assets()
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
    except FileExistsError as e:
        current_app.logger.exception(f"Publish assets FAILED: {e}")
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


def _publish_html():
    alerts = Alerts.load()
    rendered_pages = get_rendered_pages(alerts)
    upload_html_to_s3(rendered_pages)


def _publish_assets():
    upload_assets_to_s3()


def _publish_cap_xml():
    alerts = Alerts.load()
    cap_xml_alerts = get_cap_xml_for_alerts(alerts)
    upload_cap_xml_to_s3(cap_xml_alerts)
