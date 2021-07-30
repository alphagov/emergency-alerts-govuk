import pytest

from lib.alert import Alert
from tests.conftest import render_template


def test_past_alerts_page(env):
    html = render_template(env, "src/past-alerts.html")
    assert html.select_one('h1').text.strip() == "Past alerts"


@pytest.mark.parametrize('is_public,expected_title,expected_link_text', [
    [
        False,
        'Mobile network operator test',
        'More information about mobile network operator tests',
    ],
    [
        True,
        'Emergency alert sent to foo',
        'More information about this alert',
    ]
])
def test_past_alerts_page_shows_alerts(
    is_public,
    expected_title,
    expected_link_text,
    mocker,
    alert_dict,
    env
):
    alert_dict['area_names'] = ['foo']
    mocker.patch('lib.alert.Alert.is_public', is_public)
    mocker.patch('lib.alerts.Alerts.expired', [Alert(alert_dict)])

    html = render_template(env, "src/past-alerts.html")
    titles = html.select('h2.alerts-alert__title')
    link = html.select_one('a.govuk-body')

    assert len(titles) == 1
    assert titles[0].text.strip() == expected_title
    assert expected_link_text in link.text
