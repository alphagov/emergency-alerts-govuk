import logging
import os

import opentelemetry.instrumentation.auto_instrumentation.sitecustomize  # noqa
from dramatiq.middleware import (
    Callbacks,
    Middleware,
    ShutdownNotifications,
    TimeLimit,
)
from dramatiq_sqs import SQSBroker
from flask import Flask
from flask_dramatiq import AppContextMiddleware, Dramatiq
from opentelemetry import trace
from opentelemetry_instrumentor_dramatiq import DramatiqInstrumentor

from app import govuk_logging
from app.instrumentation import SqsBrokerInstrumentor
from app.notify_client.alerts_api_client import (
    alerts_api_client,
    publish_api_client,
)
from app.utils import DIST

DramatiqInstrumentor().instrument()
SqsBrokerInstrumentor().instrument()

# We override the broker when init-ing
dramatiq_instance = Dramatiq(broker_cls="dramatiq.brokers.stub:StubBroker")
_tracer = trace.get_tracer(__name__)


def create_app():
    application = Flask(
        __name__,
        static_folder=str(DIST),
    )

    from app.config import configs
    environment = os.getenv('HOST', 'local')
    application.config.from_object(configs[environment])

    from app.main import bp as main
    application.register_blueprint(main)

    from app.commands import setup_commands
    setup_commands(application)

    govuk_logging.init_app(application)
    setup_dramatiq(application)
    alerts_api_client.init_app(application)
    publish_api_client.init_app(application)

    return application


class ActorQueuePrefixMiddleware(Middleware):
    """
    Prefix the queue names of actors with a given prefix
    """

    actor_options = {"original_queue_name"}
    logger = logging.getLogger(__name__)

    def __init__(self, prefix: str = None):
        self.prefix = prefix
        self.logger.debug("Prefixing queue names with: %s", prefix)

    def before_declare_actor(self, broker, actor):
        queue_name = actor.queue_name

        # We don't want registering an actor twice to prefix twice
        if "original_queue_name" in actor.options:
            queue_name = actor.options["original_queue_name"]
        actor.options["original_queue_name"] = queue_name

        new_queue_name = self.prefix + queue_name
        self.logger.debug(
            "Prefixed queue name for actor %s: %s -> %s",
            actor.actor_name,
            actor.queue_name,
            new_queue_name,
        )
        actor.queue_name = new_queue_name


def setup_dramatiq(app):
    # flask_dramatiq provides its own @dramatiq.actor decorator
    # This has the excellent property of lazily registering so we don't actually need dramatiq
    # configured during module import. Awesome. And auto-injecting the Flask context.
    # Except asking flask_dramatiq to init doesn't give you control of the dramatiq Broker class
    # to the extent needed - only the `url` kwarg. The SQS broker doesn't use that :(

    # So we cheat here: let flask_dramatiq do its thing and then replace the stub broker instance
    # inside to what we want.
    dramatiq_instance.init_app(app)

    middleware = [
        AppContextMiddleware(app),
        ActorQueuePrefixMiddleware(prefix=app.config["QUEUE_PREFIX"]),
        # This is mostly the default_middleware - except we remove Prometheus and AgeLimit
        # ...the latter of which would re-queue messages onto the queue, but actually we want SQS
        # and its visibility timeout to do that for a single message, and redrive into a DLQ after a period.
        # i.e. let the infrastructure do the work there and not process here.
        TimeLimit(),
        ShutdownNotifications(),
        Callbacks(),
    ]
    sqs_broker = SQSBroker(
        middleware=middleware,
        visibility_timeout=None,  # Use the queue's default
    )

    dramatiq_instance.broker = sqs_broker
    for actor in dramatiq_instance.actors:
        # Re-register the actors so they reference our new broker
        actor.register(broker=sqs_broker)


def define_traced_actor(**kwargs):
    """The same as flask_dramatiq's @actor decorator, but it also automatically starts a trace."""

    def inner(fn):
        return dramatiq_instance.actor(
            _tracer.start_as_current_span(kwargs["actor_name"])(fn), **kwargs
        )

    return inner
