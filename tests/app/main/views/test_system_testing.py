import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alerts import Alerts
from app.models.planned_test import PlannedTest
from tests import normalize_spaces
from tests.conftest import create_alert_dict


def test_system_testing_page(mocker, client_get):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    html = client_get("alerts/operator-testing")
    assert html.select_one('h1').text.strip() == "Operator tests"
    assert html.select_one('main p').text.strip() == "The government and mobile network operators" \
        " occasionally carry out operator tests."


@freeze_time('2021-01-01T11:30:00Z')
@pytest.mark.parametrize('planned_tests,expected_p', [
    [
        [PlannedTest({
            'id': '1513b353-685e-488e-9547-4e1ce7359051',
            'channel': 'operator',
            'approved_at': dt_parse('2020-02-01T23:00:00Z'),
            'starts_at': dt_parse('2020-04-21T13:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2020-04-21T14:00:00Z'),
            'display_in_status_box': None,
            'status_box_content': None,
            'welsh_status_box_content': None,
            'summary': 'This summary should not be displayed',
            'welsh_summary': None,
            'content': 'This is a mobile network operator test of the Emergency Alerts '
                       'service. You do not need to take any action. To find out more, '
                       'search for gov.uk/alerts',
            'welsh_content': None,
            'areas': {'names': ['Ibiza']},
            'display_as_link': True,
            'extra_content': None
        })],
        'The government and mobile network operators occasionally carry out operator tests.'
    ],
    [
        [PlannedTest({
            'id': '1513b353-685e-488e-9547-4e1ce7359051',
            'channel': 'operator',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-04-21T13:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-04-21T14:00:00Z'),
            'display_in_status_box': None,
            'status_box_content': 'Status box content',
            'welsh_status_box_content': None,
            'summary': 'This summary should be displayed',
            'welsh_summary': None,
            'content': 'This is a mobile network operator test of the Emergency Alerts '
                       'service. You do not need to take any action. To find out more, '
                       'search for gov.uk/alerts',
            'welsh_content': None,
            'areas': {'names': ['Ibiza']},
            'display_as_link': True,
            'extra_content': None
        })],
        'This summary should be displayed'
    ]
])
def test_planned_test_summary(planned_tests, expected_p, mocker, client_get):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=planned_tests)
    html = client_get("alerts/operator-testing")
    assert html.select_one('h1').text.strip() == "Operator tests"
    assert html.select_one('main p').text.strip() == expected_p


@pytest.mark.parametrize('extra_json_fields', (
    # Doesn’t matter if the alert is still active…
    {},
    # Or if it’s cancelled before now
    {'cancelled_at': dt_parse('2021-04-21T11:00:00Z')},
    # Or if it’s finished already
    {'finishes_at': dt_parse('2021-04-21T11:00:00Z')},
))
@freeze_time('2021-04-21T09:59:00Z')
def test_system_testing_page_with_current_operator_test(
    mocker,
    client_get,
    extra_json_fields,
):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            channel='operator',
            starts_at=dt_parse('2021-04-21T09:00:00Z'),
            content='This is a mobile network operator test of the Emergency Alerts '
                    'service. You do not need to take any action. To find out more, '
                    'search for gov.uk/alerts',
            **extra_json_fields
        )
    ]))
    html = client_get("alerts/operator-testing")
    assert [
        normalize_spaces(h2.text) for h2 in html.select('.govuk-grid-column-two-thirds h2')
    ] == [
        'Wednesday 21 April 2021', '', 'Operator tests', 'Opt out of operator test alerts'
    ]
    assert [
        normalize_spaces(p.text) for p in html.select('.govuk-grid-column-two-thirds p')[:4]
    ] == [
        'There will be an operator test of the UK Emergency Alerts system today.',
        'Most mobile phones and tablets will not get a test alert.',
        'The alert will say:',
        (
            'This is a mobile network operator test of the Emergency Alerts '
            'service. You do not need to take any action. To find out more, '
            'search for gov.uk/alerts'
        )
    ]
