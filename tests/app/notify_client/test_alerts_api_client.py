from app.notify_client.alerts_api_client import AlertsApiClient


def test_get_alerts(mocker):
    client = AlertsApiClient()
    mock_get = mocker.patch.object(client, 'get')

    client.get_alerts()
    mock_get.assert_called_with(url='/govuk-alerts')
