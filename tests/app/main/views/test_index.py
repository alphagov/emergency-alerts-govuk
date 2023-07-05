import base64
import hashlib

import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.planned_test import PlannedTest
from tests.conftest import create_planned_test_dict


def test_index_page(client_get):
    html = client_get("alerts")
    assert html.select_one('h1').text.strip() == "About Emergency Alerts"
    assert 'current alert' not in html.select('.govuk-heading-m')


@pytest.mark.parametrize('planned_tests', (
    ([]),
    ([
        PlannedTest(create_planned_test_dict()),
    ]),
))
def test_index_page_shows_current_alerts(
    client_get,
    mocker,
    alert_dict,
    planned_tests,
):
    mocker.patch('app.models.alerts.Alerts.current_and_public', ['alert'])
    mocker.patch('app.models.alerts.Alerts.last_updated_date')
    html = client_get("alerts")
    assert '1 current alert' in html.text
    # Test alerts should not show on homepage when there is a current alert
    assert 'service test' not in html.select_one('main h2').text.lower()


@freeze_time('2021-01-01T11:30:00Z')
@pytest.mark.parametrize('data_from_yaml,expected_h2', [
    [
        [PlannedTest({
            'id': '1513b353-685e-488e-9547-4e1ce7359051',
            'channel': 'severe',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-04-21T13:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-04-21T14:00:00Z'),
            'display_in_status_box': True,
            'status_box_content': None,
            'welsh_status_box_content': None,
            'summary': None,
            'welsh_summary': None,
            'content': 'This is a mobile network operator test of the Emergency Alerts '
                       'service. You do not need to take any action. To find out more, '
                       'search for gov.uk/alerts',
            'welsh_content': None,
            'areas': {'names': ['Ibiza']}
        })],
        'On Wednesday 21 April 2021 at 2PM, there will be a test of the UK Emergency Alerts service'
    ],
    [
        [PlannedTest({
            'id': '1513b353-685e-488e-9547-4e1ce7359051',
            'channel': 'severe',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-04-21T13:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-04-21T14:00:00Z'),
            'display_in_status_box': True,
            'status_box_content': 'Status box content',
            'welsh_status_box_content': None,
            'summary': None,
            'welsh_summary': None,
            'content': 'This is a mobile network operator test of the Emergency Alerts '
                       'service. You do not need to take any action. To find out more, '
                       'search for gov.uk/alerts',
            'welsh_content': None,
            'areas': {'names': ['Ibiza']}
        })],
        'Status box content'
    ]
])
def test_index_page_shows_announcements(
    data_from_yaml,
    expected_h2,
    client_get,
    mocker
):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=data_from_yaml)
    html = client_get("alerts")
    assert expected_h2.lower() \
        in html.select_one('main h2').text.lower()


def test_index_page_content_security_policy_sha(client_get):
    script_sha256_base64_encoded = b"+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU="

    html = client_get("alerts")
    inline_script = html.select_one('body > script')

    assert inline_script is not None
    script_code = inline_script.string.strip()

    # generate the sha256 of the script code and base64 encode it
    script_code_sha256 = base64.b64encode(
        hashlib.sha256(script_code.encode('utf-8')).digest()
    )

    assert script_code_sha256 == script_sha256_base64_encoded
