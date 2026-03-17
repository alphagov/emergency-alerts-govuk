from dateutil.parser import parse as dt_parse
from notifications_python_client.base import BaseAPIClient


class _BaseAlertsClient(BaseAPIClient):
    # Base class for the below API clients.
    # Any subclasses must set `api_key_config_name` to the key in config accordingly

    def __init__(self) -> None:
        super().__init__("a" * 73, "b")

    def init_app(self, app) -> None:
        self.base_url = app.config["NOTIFY_API_HOST_NAME"]
        self.api_key = app.config[self.api_key_config_name]
        self.service_id = app.config[self.api_key_client_config_name]


class AlertsApiClient(_BaseAlertsClient):
    TIMESTAMP_FIELDS = [
        'approved_at',
        'starts_at',
        'cancelled_at',
        'finishes_at'
    ]

    api_key_config_name = "GOVUK_CLIENT_SECRET"
    api_key_client_config_name = "NOTIFY_API_CLIENT_ID"

    def get_alerts(self):
        data = self.get(url='/govuk-alerts')['alerts']

        for alert_dict in data:
            for field in self.TIMESTAMP_FIELDS:
                if alert_dict[field]:
                    alert_dict[field] = dt_parse(alert_dict[field])

        return data

    def send_publish_acknowledgement(self):
        return self.post(url="/govuk-alerts/acknowledge", data={})


alerts_api_client = AlertsApiClient()


class AlertsPublishApiClient(_BaseAlertsClient):

    api_key_config_name = "GOVUK_ALERTS_PUBLISH_CLIENT_SECRET"
    api_key_client_config_name = "GOVUK_ALERTS_PUBLISH_CLIENT_ID"

    # The following client methods post data to API (specifically `publish_task_progress` endpoints)
    # and are used to update state of Publish Progress Tasks in DB

    def create_publish_task(self, task_id):
        # Creates publish progress task in the database and returns data stored for the task
        return self.post(url="/publish_task_progress/add-publish", data={"task_id": task_id})

    def get_publish_task(self, id):
        # Retrieves a specific publish progress task's data from the database
        return self.post(url="/publish_task_progress/get-publish", data={"id": id})

    def update_publish_task(self, id, file):
        # Updates the `last_activity_at` and `last_published_file` attributes of publish progress task in the database
        return self.post(url="/publish_task_progress/update-publish", data={"id": id, "file": file})

    def mark_publish_as_finished(self, id):
        # Updates the `finished_at` attribute of publish progress task in the database
        self.post(url="/publish_task_progress/finish-publish", data={"id": id})


publish_api_client = AlertsPublishApiClient()
