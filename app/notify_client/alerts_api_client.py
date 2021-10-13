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
        self.api_key = app.config['NOTIFY_API_CLIENT_SECRET']
        self.service_id = app.config['NOTIFY_API_CLIENT_ID']

    def get_alerts(self):
        data = self.get(url='/govuk-alerts')['alerts']

        for alert_dict in data:
            for field in self.TIMESTAMP_FIELDS:
                if alert_dict[field]:
                    alert_dict[field] = dt_parse(alert_dict[field])

        return data
