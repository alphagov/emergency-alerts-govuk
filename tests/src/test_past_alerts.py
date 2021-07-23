from bs4 import BeautifulSoup

from lib.alert import Alert


def test_past_alerts_page(env):
    template = env.get_template("src/past-alerts.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert html.select_one('h1').text.strip() == "Past alerts"


def test_past_alerts_page_shows_alerts(
    mocker,
    alert_dict,
    env
):
    mocker.patch('lib.alerts.Alerts.expired_or_test', [Alert(alert_dict)])
    template = env.get_template("src/past-alerts.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert len(html.select('h2.alerts-alert__title')) == 1
