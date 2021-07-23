from bs4 import BeautifulSoup

from lib.alert import Alert


def test_current_alerts_page(env):
    template = env.get_template("src/current-alerts.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert html.select_one('h1').text.strip() == "Current alerts"


def test_current_alerts_page_shows_alerts(
    alert_dict,
    env,
    mocker,
):
    mocker.patch('lib.alerts.Alerts.current_public', [Alert(alert_dict)])
    template = env.get_template("src/current-alerts.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert len(html.select('h2.alerts-alert__title')) == 1
