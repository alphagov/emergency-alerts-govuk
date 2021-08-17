def test_index_page(client_get):
    html = client_get("alerts")
    assert html.select_one('h1').text.strip() == "Emergency Alerts"
    assert 'current alert' not in html.text


def test_index_page_shows_current_alerts(client_get, mocker, alert_dict):
    mocker.patch('app.models.alerts.Alerts.current_and_public', ['alert'])
    mocker.patch('app.models.alerts.Alerts.last_updated_date')
    html = client_get("alerts")
    assert '1 current alert' in html.text
