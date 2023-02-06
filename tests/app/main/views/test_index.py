import base64
import hashlib

import pytest

from app.models.planned_test import PlannedTest
from tests import normalize_spaces
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
    mocker.patch('app.models.alerts.Alerts.current_and_planned_test_alerts', planned_tests)
    mocker.patch('app.models.alerts.Alerts.last_updated_date')
    html = client_get("alerts")
    assert '1 current alert' in html.text
    # Test alerts should not show on homepage when there is a current alert
    assert 'planned test' not in html.select_one('main h2').text.lower()


@pytest.mark.parametrize('current_and_planned_test_alerts, expected_banner', (
    ([
        PlannedTest(create_planned_test_dict(
            starts_at='2021-02-03T00:00:00Z'
        ))
    ], (
        '1 planned test '
        'Wednesday 3 February 2021'
    )),
    ([
        PlannedTest(create_planned_test_dict(
            starts_at='2021-02-03T00:00:00Z'
        )),
        PlannedTest(create_planned_test_dict(
            starts_at='2021-06-03T00:00:00Z'
        )),
    ], (
        '2 planned tests '
        'Wednesday 3 February 2021 and Thursday 3 June 2021'
    )),
    ([
        PlannedTest(create_planned_test_dict(
            starts_at='2021-02-03T00:00:00Z'
        )),
        PlannedTest(create_planned_test_dict(
            starts_at='2021-06-03T00:00:00Z'
        )),
        PlannedTest(create_planned_test_dict(
            starts_at='2021-06-03T23:00:01Z'
        )),
    ], (
        '3 planned tests '
        'Wednesday 3 February 2021 to Friday 4 June 2021'
    )),
))
def test_index_page_shows_planned_tests(
    client_get,
    mocker,
    current_and_planned_test_alerts,
    expected_banner,
):
    mocker.patch('app.models.alerts.Alerts.current_and_public', [])
    mocker.patch(
        'app.models.alerts.Alerts.current_and_planned_test_alerts',
        current_and_planned_test_alerts,
    )

    html = client_get("alerts")
    assert normalize_spaces(
        html.select_one('.alerts-notification-banner').text
    ) == (
        expected_banner
    )

    assert html.select_one('.alerts-notification-banner a')['href'] == (
        '/alerts/planned-tests'
    )


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
