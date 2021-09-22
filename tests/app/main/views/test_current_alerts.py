
from app.models.alerts import Alerts


def test_current_alerts_page(client_get):
    html = client_get("alerts/current-alerts")
    assert html.select_one('h1').text.strip() == "Current alerts"


def test_current_alerts_page_shows_alerts(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch('app.models.alert.Alert.display_areas', ['foo'])
    mocker.patch('app.models.alert.Alert.is_current_and_public', return_value=True)
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select('h2.alerts-alert__title')
    link = html.select_one('a.govuk-body')

    assert len(titles) == 1
    assert titles[0].text.strip() == 'Emergency alert sent to foo'
    assert 'More information about this alert' in link.text
