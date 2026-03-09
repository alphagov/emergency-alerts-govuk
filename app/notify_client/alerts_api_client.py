from dateutil.parser import parse as dt_parse
from notifications_python_client.base import BaseAPIClient


class AlertsApiClient(BaseAPIClient):
    TIMESTAMP_FIELDS = [
        'approved_at',
        'starts_at',
        'cancelled_at',
        'finishes_at'
    ]

    def __init__(self):
        super().__init__("a" * 73, "b")

    def init_app(self, app):
        self.base_url = app.config['NOTIFY_API_HOST_NAME']
        self.api_key = app.config["GOVUK_CLIENT_SECRET"]
        self.service_id = app.config['NOTIFY_API_CLIENT_ID']

    def get_alerts(self):
        data = self.get(url='/govuk-alerts')['alerts']

        for alert_dict in data:
            for field in self.TIMESTAMP_FIELDS:
                if alert_dict[field]:
                    alert_dict[field] = dt_parse(alert_dict[field])

        return data

    def send_publish_acknowledgement(self):
        return self.post(url="/govuk-alerts/acknowledge", data={})

    # The following client methods post data to API (specifically `publish_task_progress` endpoints)
    # and are used to update state of Publish Progress Tasks in DB

    def create_publish_task(self, task_id):
        # Creates publish progress task in the database and returns data stored for the task
        return self.post(url="/publish_task_progress/add-publish", data={"task_id": task_id})

    def get_publish_task(self, task_id):
        # Retrieves a specific publish progress task's data from the database
        return self.post(url="/publish_task_progress/get-publish", data={"task_id": task_id})

    def update_publish_task(self, task_id, file):
        # Updates the `last_activity_at` and `last_published_file` attributes of publish progress task in the database
        return self.post(url="/publish_task_progress/update-publish", data={"task_id": task_id, "file": file})

    def mark_publish_as_finished(self, task_id):
        # Updates the `finished_at` attribute of publish progress task in the database
        self.post(url="/publish_task_progress/finish-publish", data={"task_id": task_id})


alerts_api_client = AlertsApiClient()
