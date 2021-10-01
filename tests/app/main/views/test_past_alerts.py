from datetime import datetime

import pytest
import pytz

from app.models.alert import Alert


def test_past_alerts_page(client_get):
    html = client_get("alerts/past-alerts")
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
    client_get
):
    mocker.patch('app.models.alert.Alert.display_areas', ['foo'])
    mocker.patch('app.models.alert.Alert.is_public', is_public)
    mocker.patch('app.models.alerts.Alerts.expired', [Alert(alert_dict)])

    html = client_get("alerts/past-alerts")
    titles = html.select('h3.alerts-alert__title')
    link = html.select_one('a.govuk-body')

    assert len(titles) == 1
    assert titles[0].text.strip() == expected_title
    assert expected_link_text in link.text


def test_past_alerts_page_groups_by_date(
    mocker,
    alert_dict,
    client_get,
):
    alert_dict_2 = alert_dict.copy()
    alert_dict_3 = alert_dict.copy()
    alert_dict_4 = alert_dict.copy()

    alert_dict_2['starts_at'] = datetime(2021, 4, 22, 0, 0, tzinfo=pytz.utc)
    alert_dict_2['content'] = 'Something 2'

    alert_dict_3['starts_at'] = datetime(2021, 4, 22, 22, 59, tzinfo=pytz.utc)
    alert_dict_3['content'] = 'Something 3'

    alert_dict_4['channel'] = 'operator'
    alert_dict_4['content'] = 'Operator test'

    mocker.patch('app.models.alert.Alert.display_areas', ['foo'])
    mocker.patch('app.models.alerts.Alerts.expired', [
        Alert(alert_dict),
        Alert(alert_dict),
        Alert(alert_dict_2),
        Alert(alert_dict_3),
        Alert(alert_dict_4),
        Alert(alert_dict_4),
    ])

    html = client_get("alerts/past-alerts")
    titles_and_paragraphs = html.select('main h2.govuk-heading-m, main p.govuk-body-l')
    assert [
        element.text.strip() for element in titles_and_paragraphs
    ] == [
        'Thursday 22 April 2021',
        'Something 3',
        'Something 2',
        'Wednesday 21 April 2021',
        # Multiple public alerts are shown individually
        'Something',
        'Something',
        # Multiple non-public alerts on the same day are combined into one
        'Operator test',
    ]
