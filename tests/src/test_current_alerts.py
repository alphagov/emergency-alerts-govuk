from lib.alert import Alert
from tests.conftest import render_template


def test_current_alerts_page(env):
    html = render_template(env, "src/current-alerts.html")
    assert html.select_one('h1').text.strip() == "Current alerts"


def test_current_alerts_page_shows_alerts(
    alert_dict,
    env,
    mocker,
):
    mocker.patch('lib.alerts.Alerts.current_public', [Alert(alert_dict)])
    html = render_template(env, "src/current-alerts.html")
    assert len(html.select('h2.alerts-alert__title')) == 1
