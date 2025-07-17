from uuid import UUID

import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alerts import Alerts
from tests.conftest import create_alert_dict


def test_past_alerts_page(client_get):
    html = client_get("alerts/past-alerts")
    assert html.select_one('h1').text.strip() == "Past alerts"


@freeze_time('2021-04-23T11:00:00Z')
@pytest.mark.parametrize('is_public,expected_title', [
    [
        True,
        'Emergency alert sent to Foo',
    ]
])
def test_past_alerts_page_shows_single_past_alert(
    is_public,
    expected_title,
    mocker,
    alert_dict,
    client_get
):
    mocker.patch('app.models.alert.Alert.display_areas', ['foo'])
    mocker.patch('app.models.alert.Alert.is_public', is_public)
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([alert_dict]))

    html = client_get("alerts/past-alerts")
    titles = html.select('h3.alerts-alert__title')

    assert len(titles) == 1
    assert titles[0].text.strip() == expected_title


@freeze_time('2021-04-23T11:00:00Z')
@pytest.mark.parametrize('is_public,expected_title,expected_link_text', [
    [
        True,
        'Emergency alert sent to Foo',
        'More information about this alert',
    ]
])
def test_past_alerts_page_shows_multiple_past_alerts(
    is_public,
    expected_title,
    expected_link_text,
    mocker,
    alert_dict,
    client_get
):
    mocker.patch('app.models.alert.Alert.display_areas', ['foo'])
    mocker.patch('app.models.alert.Alert.is_public', is_public)
    content = """This is a mobile network operator test of the Emergency Alerts service.
    You do not need to take any action. To find out more, search for gov.uk/alerts"""
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([create_alert_dict(content=content), alert_dict]))

    html = client_get("alerts/past-alerts")
    titles = html.select('h3.alerts-alert__title')
    truncated_content = html.select('p.truncated-text')
    links = html.select('a.govuk-body')

    assert len(titles) == 2
    assert titles[0].text.strip() == expected_title
    assert truncated_content[0].text.strip() == content
    assert truncated_content[1].text.strip() == "Something"
    assert len(links) == 2
    if is_public:
        assert expected_link_text in links[0].text
        assert expected_link_text in links[1].text


@freeze_time('2021-04-24T11:00:00Z')
def test_past_alerts_does_not_show_archived(
    mocker,
    client_get,
):
    alerts = [
        create_alert_dict(id=UUID(int=1), content='Something 1', starts_at=dt_parse('2021-04-21T11:00:00Z')),
        create_alert_dict(id=UUID(int=2), content='Something 1', starts_at=dt_parse('2021-04-21T11:00:00Z')),
        create_alert_dict(id=UUID(int=3), channel='operator', starts_at=dt_parse('2021-04-21T11:00:00Z'), content='Operator test'),  # noqa
        create_alert_dict(id=UUID(int=4), channel='operator', starts_at=dt_parse('2021-04-21T11:00:00Z'), content='Operator test'),  # noqa
        create_alert_dict(id=UUID(int=5), channel='operator', starts_at=dt_parse('2021-04-22T12:00:00Z'), content='Operator test'),  # noqa
        create_alert_dict(id=UUID(int=6), channel='operator', starts_at=dt_parse('2021-04-22T10:00:00Z'), content='Operator test'),  # noqa
    ]
    # set all alerts to cancelled so they show in past alerts
    for alert in alerts:
        alert['cancelled_at'] = alert['starts_at']

    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts(alerts))

    html = client_get("alerts/past-alerts")
    titles_and_paragraphs = html.select('main .govuk-grid-column-two-thirds h2.govuk-heading-m, \
        main .govuk-grid-column-two-thirds p.govuk-body-l')
    assert [
        element.text.strip() for element in titles_and_paragraphs
    ] == [
        # Only public alerts show after over 48 hours, not service tests
        'Wednesday 21 April 2021',
        'Something 1',
        'Something 1',
    ]


@freeze_time('2021-04-23T11:00:00Z')
def test_past_alerts_page_groups_by_date(
    mocker,
    client_get,
):
    alerts = [
        create_alert_dict(id=UUID(int=1), content='Something 1', starts_at=dt_parse('2021-04-21T11:00:00Z')),
        create_alert_dict(id=UUID(int=2), content='Something 1', starts_at=dt_parse('2021-04-21T11:00:00Z')),
        create_alert_dict(id=UUID(int=3), content='Something 2', starts_at=dt_parse('2021-04-22T00:00:00Z')),
        create_alert_dict(id=UUID(int=4), content='Something 3', starts_at=dt_parse('2021-04-22T22:59:00Z')),
        create_alert_dict(id=UUID(int=3), content='Something 4', starts_at=dt_parse('2021-04-23T00:00:00Z')),
        create_alert_dict(id=UUID(int=4), content='Something 5', starts_at=dt_parse('2021-04-23T22:59:00Z')),
        create_alert_dict(id=UUID(int=5), channel='operator', starts_at=dt_parse('2021-04-21T12:00:00Z'), content='Operator test'),  # noqa
        create_alert_dict(id=UUID(int=6), channel='operator', starts_at=dt_parse('2021-04-21T12:00:00Z'), content='Operator test'),  # noqa
    ]
    # set all alerts to cancelled so they show in past alerts
    for alert in alerts:
        alert['cancelled_at'] = alert['starts_at']

    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts(alerts))

    html = client_get("alerts/past-alerts")
    titles_and_paragraphs = html.select('main .govuk-grid-column-two-thirds h2.govuk-heading-m, \
        main .govuk-grid-column-two-thirds p.govuk-body-l')
    assert [
        element.text.strip() for element in titles_and_paragraphs
    ] == [
        'Friday 23 April 2021',
        'Something 4',  # Only alert that day that appears before test timestamp
        'Something 3',
        'Something 2',
        # Multiple public alerts are shown individually
        'Something 1',
        'Something 1',
    ]

    older_dates = html.select('main .govuk-grid-column-two-thirds h2.date-margin-top')
    # Asserts that the older dates that appear on past alert page have date-margin-top class,
    # a custom class that ensures margin-top is applied, if date isn't most recent
    assert [
        element.text.strip() for element in older_dates
    ] == ['Thursday 22 April 2021', 'Wednesday 21 April 2021']
