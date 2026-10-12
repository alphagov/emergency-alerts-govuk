# isort: skip_file
# Called by the Dramatiq CLI as an importable module for workers

# Get a created init-ed Flask app
import app

app.create_app()

# Import so that the decorators run and register the actors
import app.tasks.tasks # noqa

# By importing app we will have init-ed the flask_dramatiq package
# ...and then we can steal its broker here to present to the worker process.
broker = app.dramatiq_instance.broker
