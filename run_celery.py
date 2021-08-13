from app import create_app, notify_celery  # noqa

application = create_app()
application.app_context().push()
