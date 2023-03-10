import click

from flask import current_app
from flask import cli

from app.utils import purge_fastly_cache, upload_to_s3, upload_assets_to_s3


def setup_commands(app):
    app.cli.add_command(publish)


@click.command('publish')
@cli.with_appcontext
def publish():
    try:
        upload_to_s3()
        purge_fastly_cache()
    except Exception as e:
        current_app.logger.exception("Publish FAILED: {e}")


@click.command('publish-with-assets')
@cli.with_appcontext
def publish_with_assets():
    try:
        upload_to_s3()
        upload_assets_to_s3()
        purge_fastly_cache()
    except FileExistsError as e:
        current_app.logger.exception(f"Publish assets FAILED: {e}")
    except Exception as e:
        current_app.logger.exception(f"Publish FAILED: {e}")
