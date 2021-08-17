import click

from app.celery.tasks import publish_govuk_alerts


def setup_commands(app):
    app.cli.add_command(publish)


@click.command('publish')
def publish():
    publish_govuk_alerts()
