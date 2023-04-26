from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alerts import Alerts
from tests import normalize_spaces
from tests.conftest import create_alert_dict


def test_planned_tests_page(mocker, client_get):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    html = client_get("alerts/service-tests")
    assert html.select_one('h1').text.strip() == "Service tests"
    assert [
        normalize_spaces(p.text) for p in html.select('main p')
    ] == [
        'There are currently no service tests.'
    ]


@freeze_time('2021-04-21T11:00:00Z')
def test_planned_tests_page_with_previous_days_operator_test(
    mocker,
    client_get,
):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            channel='operator',
            starts_at=dt_parse('2021-04-20T09:00:00Z'),
            finishes_at=dt_parse('2021-04-20T10:00:00Z'),
            cancelled_at=None,
        )
    ]))
    html = client_get("alerts/service-tests")
    assert normalize_spaces(html.select_one('main p').text) == (
        'There are currently no service tests.'
    )
