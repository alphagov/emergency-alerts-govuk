import click
from flask import cli, current_app

from app.models.alerts import Alerts
from app.notify_client.alerts_api_client import alerts_api_client
from app.render import get_cap_xml_for_alerts, get_rendered_pages
from app.utils import (
    create_publish_healthcheck_filename,
    delete_timestamp_file_from_s3,
    purge_fastly_cache,
    put_success_metric_data,
    put_timestamp_to_s3,
    setup_s3_session,
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
        publish_healthcheck_filename = create_publish_healthcheck_filename(
            "publish-dynamic",
            "cli"
        )
        _publish_html(publish_healthcheck_filename)
        purge_fastly_cache()
        alerts_api_client.send_publish_acknowledgement()
        delete_timestamp_file_from_s3(publish_healthcheck_filename)
        put_success_metric_data("publish-dynamic")
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


@click.command('publish-with-assets')
@click.option("--startup", is_flag=True)
@cli.with_appcontext
def publish_with_assets(startup):
    try:
        origin = "startup" if startup else "cli"
        publish_healthcheck_filename = create_publish_healthcheck_filename(
            "publish-all",
            origin
        )

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


def _publish_html(publish_healthcheck_filename=None):
    s3_session = None

    if publish_healthcheck_filename:
        s3_session = setup_s3_session()
        # Initial write of timestamp to file to mark the start of the publish
        put_timestamp_to_s3(publish_healthcheck_filename, s3_session)

    current_app.logger.info("Starting load of alerts")
    alerts = Alerts.load(
        publish_healthcheck_filename,
        s3_session,
    )
    current_app.logger.info("Starting render of pages")
    rendered_pages = get_rendered_pages(alerts)
    current_app.logger.info("Ending render of pages")
    upload_html_to_s3(rendered_pages, publish_healthcheck_filename, s3_session=s3_session)


def _publish_assets(publish_healthcheck_filename=None):
    s3_session = None
    if publish_healthcheck_filename:
        s3_session = setup_s3_session()
        # Initial write of timestamp to file to mark the start of the publish
        put_timestamp_to_s3(publish_healthcheck_filename, s3_session)
    upload_assets_to_s3(publish_healthcheck_filename, s3_session)


def _publish_cap_xml(publish_healthcheck_filename):
    s3_session = None

    if publish_healthcheck_filename:
        s3_session = setup_s3_session()
        # Initial write of timestamp to file to mark the start of the publish
        put_timestamp_to_s3(publish_healthcheck_filename, s3_session)

    alerts = Alerts.load(
        publish_healthcheck_filename,
        s3_session,
    )
    cap_xml_alerts = get_cap_xml_for_alerts(alerts)
    upload_cap_xml_to_s3(
        cap_xml_alerts,
        publish_healthcheck_filename,
        s3_session=s3_session,
    )
