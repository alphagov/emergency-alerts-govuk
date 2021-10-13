from datetime import datetime

from app.notify_client.alerts_api_client import AlertsApiClient
from tests.conftest import create_alert_dict


def test_get_alerts(mocker):
    response = {'alerts': [
        create_alert_dict(
            approved_at='2020-01-01T01:01:00Z',
            cancelled_at='2020-01-01T01:01:00Z',
            finishes_at='2020-01-01T01:01:00Z',
            starts_at='2020-01-01T01:01:00Z',
        )
    ]}

    client = AlertsApiClient()
    mock_get = mocker.patch.object(client, 'get', return_value=response)

    alert_dicts = client.get_alerts()
    mock_get.assert_called_with(url='/govuk-alerts')

    assert len(alert_dicts) == 1
    assert isinstance(alert_dicts[0]['approved_at'], datetime)
    assert isinstance(alert_dicts[0]['finishes_at'], datetime)
    assert isinstance(alert_dicts[0]['cancelled_at'], datetime)
    assert isinstance(alert_dicts[0]['starts_at'], datetime)


def test_get_alerts_ignores_blank_timestamps(mocker):
    response = {'alerts': [
        create_alert_dict(
            approved_at='2020-01-01T01:01:00Z',
            finishes_at='2020-01-01T01:01:00Z',
            starts_at='2020-01-01T01:01:00Z',
            cancelled_at=None,
        )
    ]}

    client = AlertsApiClient()
    mocker.patch.object(client, 'get', return_value=response)

    alert_dicts = client.get_alerts()
    assert alert_dicts[0]['cancelled_at'] is None
