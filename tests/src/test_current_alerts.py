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
    alert_dict['areas']['aggregate_names'] = ['foo']
    mocker.patch('lib.alerts.Alerts.current_and_public', [Alert(alert_dict)])

    html = render_template(env, "src/current-alerts.html")
    titles = html.select('h2.alerts-alert__title')
    link = html.select_one('a.govuk-body')

    assert len(titles) == 1
    assert titles[0].text.strip() == 'Emergency alert sent to foo'
    assert 'More information about this alert' in link.text
