import click
import os

from flask import cli, current_app

from app.models.alerts import Alerts
from app.render import get_rendered_pages
from app.utils import purge_fastly_cache, upload_assets_to_s3, upload_html_to_s3


def setup_commands(app):
    app.cli.add_command(publish)
    app.cli.add_command(publish_with_assets)


@click.command('publish')
@cli.with_appcontext
def publish():
    try:
        _publish_html()
        if os.environ.get('ENVIRONMENT') != 'development' or os.environ.get('ENVIRONMENT') != 'preview':
            purge_fastly_cache()
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")


@click.command('publish-with-assets')
@cli.with_appcontext
def publish_with_assets():
    try:
        _publish_html()
        _publish_assets()
        purge_fastly_cache()
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
