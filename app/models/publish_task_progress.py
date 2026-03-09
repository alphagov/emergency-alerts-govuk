import time
from datetime import datetime

from emergency_alerts_utils.serialised_model import SerialisedModel

from app.notify_client.alerts_api_client import alerts_api_client


class PublishTaskProgress(SerialisedModel):

    # `PublishTaskProgress` instances represent the progress of a gov.uk/alerts publish.
    # This model allows us to store the state of the publish tasks and modify state in the database,
    # using the API client methods within classmethods.

    ALLOWED_PROPERTIES = {
        "id",  # The `task_id` for the publish task
        "started_at",  # When the publish progress task was created, in RFC 2822 format
        "last_published_at",  # When the publish progress task was last updated, in RFC 2822 format
        "last_published_file",  # The filename, or description of action, that occured with last update to the task
        "finished_at"  # When the publish progress task finished, in RFC 2822 format
    }

    def __init__(
        self,
        id,
        started_at,
        last_published_at=None,
        last_published_file=None,
        finished_at=None,
    ):
        self.id = id
        self.started_at = started_at
        self.last_published_at = last_published_at
        self.last_published_file = last_published_file
        self.finished_at = finished_at

    @classmethod
    def create(cls, publish_type, publish_origin):
        # `task_id` is combination of publish type, origin and start time and is stored
        # as `id` in the database
        task_id = f"{publish_type}_{publish_origin}_{int(time.time())}.txt"
        data = alerts_api_client.create_publish_task(task_id)
        return cls(
            id=data["id"],
            started_at=data["started_at"]
        )

    @classmethod
    def update(cls, publish_task, file):
        alerts_api_client.update_publish_task(publish_task.id, file)

    @classmethod
    def set_to_finished(cls, task_id):
        alerts_api_client.mark_publish_as_finished(task_id)

    @classmethod
    def from_id(cls, task_id):
        data = alerts_api_client.get_publish_task(task_id)
        return cls(
            id=data["id"],
            started_at=data["started_at"],
            last_published_at=data["last_published_at"],
            last_published_file=data.get("last_published_file"),
            finished_at=data.get("finished_at"),
        )

    @classmethod
    def update_progress(cls, publish_task, file):
        if cls.skip_update_via_API(publish_task):
            # Too soon since last update; skip calling the API
            return publish_task

        data = alerts_api_client.update_publish_task(publish_task.id, file)
        publish_task.last_published_file = data.get("last_published_file")
        publish_task.last_published_at = data.get(
            "last_published_at",
            publish_task.last_published_at,
        )
        return publish_task

    @classmethod
    def parse_last_published_at(cls, last_published_at):
        # If `last_published_at` has been set, here we convert it to timestamp
        if not last_published_at:
            return None
        # timestamp string returned by API has format "Mon, 09 Mar 2026 14:05:01 GMT", RFC 2822 format
        dt = datetime.strptime(last_published_at, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.timestamp()

    @classmethod
    def skip_update_via_API(cls, publish_task, min_interval_seconds=1.0):
        # Task's `last_published_at` attribute, if it has been set, is converted
        # to timestamp and compared with current timestamp
        # If `last_published_at` is less than `min_interval_seconds` ago then no need to call API,
        # to minimise calls to API
        last_published_at_datetime = cls.parse_last_published_at(publish_task.last_published_at)
        if last_published_at_datetime is None:
            return False
        return (time.time() - last_published_at_datetime) < min_interval_seconds
