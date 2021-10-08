from notifications_python_client.base import BaseAPIClient


class AlertsApiClient(BaseAPIClient):
    def __init__(self):
        super().__init__("a" * 73, "b")

    def init_app(self, app):
        self.base_url = app.config['NOTIFY_API_HOST_NAME']
        self.api_key = app.config['NOTIFY_API_CLIENT_SECRET']
        self.service_id = app.config['NOTIFY_API_CLIENT_ID']

    def get_alerts(self):
        return self.get(url='/govuk-alerts')['alerts']
