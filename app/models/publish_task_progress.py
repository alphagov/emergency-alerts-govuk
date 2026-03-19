import time
from datetime import datetime

from emergency_alerts_utils.serialised_model import SerialisedModel

from app.notify_client.alerts_api_client import publish_api_client


class PublishTaskProgress(SerialisedModel):

    # `PublishTaskProgress` instances represent the progress of a gov.uk/alerts publish.
    # This model allows us to store the state of the publish tasks and modify state in the database,
    # using the API client methods within classmethods.

    ALLOWED_PROPERTIES = {
        "task_id",  # The `task_id` for the publish task
        "started_at",  # When the publish progress task was created, in RFC 2822 format
        "last_activity_at",  # When the publish progress task was last updated, in RFC 2822 format
        "last_published_file",  # The filename, or description of action, that occured with last update to the task
        "finished_at"  # When the publish progress task finished, in RFC 2822 format
    }

    def __init__(
        self,
        id,
        task_id,
        started_at,
        last_activity_at=None,
        last_published_file=None,
        finished_at=None,
    ):
        self.id = id
        self.task_id = task_id
        self.started_at = started_at
        self.last_activity_at = last_activity_at
        self.last_published_file = last_published_file
        self.finished_at = finished_at

    @classmethod
    def create(cls, publish_type, publish_origin):
        # `task_id` is combination of publish type, origin and start time and is stored
        # as `id` in the database
        task_id = f"{publish_type}_{publish_origin}_{int(time.time())}"
        data = publish_api_client.create_publish_task(task_id)
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            started_at=data["started_at"]
        )

    @classmethod
    def from_id(cls, id):
        data = publish_api_client.get_publish_task(id)
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            started_at=data["started_at"],
            last_activity_at=data["last_activity_at"],
            last_published_file=data.get("last_published_file"),
            finished_at=data.get("finished_at"),
        )

    def update(self, file):
        publish_api_client.update_publish_task(self.id, file)

    def set_to_finished(self):
        publish_api_client.mark_publish_as_finished(self.id)

    def update_progress(self, file):
        if self.skip_update_via_API():
            # Too soon since last update; skip calling the API
            print(self)
            return self

        data = publish_api_client.update_publish_task(self.id, file)
        self.last_published_file = data.get("last_published_file")
        self.last_activity_at = data.get(
            "last_activity_at",
            self.last_activity_at,
        )
        return self

    def skip_update_via_API(self, min_interval_seconds=1.0):
        # Task's `last_activity_at` attribute, if it has been set, is converted
        # to timestamp and compared with current timestamp
        # If `last_activity_at` is less than `min_interval_seconds` ago then no need to call API,
        # to minimise calls to API
        last_activity_at_datetime = parse_last_activity_at(self.last_activity_at)
        if last_activity_at_datetime is None:
            return False
        return (time.time() - last_activity_at_datetime) < min_interval_seconds


def update_publish_progress_if_exists(publish_task_progress, path):
    if publish_task_progress:
        publish_task_progress.update_progress(file=path)


def parse_last_activity_at(last_activity_at):
    # If `last_activity_at` has been set, here we convert it to timestamp
    if not last_activity_at:
        return None
    # timestamp string returned by API has format "Mon, 09 Mar 2026 14:05:01 GMT", RFC 2822 format
    dt = datetime.strptime(last_activity_at, "%a, %d %b %Y %H:%M:%S %Z")
    return dt.timestamp()
