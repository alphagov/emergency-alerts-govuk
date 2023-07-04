import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alerts import Alerts
from tests import normalize_spaces
from tests.conftest import create_alert_dict


def test_system_testing_page(mocker, client_get):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    html = client_get("alerts/system-testing")
    assert html.select_one('h1').text.strip() == "Testing the Emergency Alerts service"
    assert html.select_one('main p').text.strip() == "Following the successful national test of the UK Emergency " \
        "Alerts system on 23 April 2023, the government and mobile network operators will be carrying out " \
        "occasional ‘operator’ tests."


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
    html = client_get("alerts/system-testing")
    assert [
        normalize_spaces(h2.text) for h2 in html.select('.govuk-grid-column-two-thirds h2')
    ] == [
        'Wednesday 21 April 2021', '', 'Operator tests', 'Opt out of operator test alerts'
    ]
    assert not html.select('main h3')
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
