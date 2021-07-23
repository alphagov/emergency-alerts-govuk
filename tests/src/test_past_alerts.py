from lib.alert import Alert
from tests.conftest import render_template


def test_past_alerts_page(env):
    html = render_template(env, "src/past-alerts.html")
    assert html.select_one('h1').text.strip() == "Past alerts"


def test_past_alerts_page_shows_alerts(
    mocker,
    alert_dict,
    env
):
    mocker.patch('lib.alerts.Alerts.expired_or_test', [Alert(alert_dict)])
    html = render_template(env, "src/past-alerts.html")
    assert len(html.select('h2.alerts-alert__title')) == 1
