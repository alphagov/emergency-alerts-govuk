from tests.conftest import render_template


def test_index_page(env):
    html = render_template(env, "src/index.html")
    assert html.select_one('h1').text.strip() == "Emergency Alerts"
    assert 'current alert' not in html.text


def test_index_page_shows_current_alerts(env, mocker, alert_dict):
    mocker.patch('app.models.alerts.Alerts.current_and_public', ['alert'])
    mocker.patch('app.models.alerts.Alerts.last_updated_date')
    html = render_template(env, "src/index.html")
    assert '1 current alert' in html.text
