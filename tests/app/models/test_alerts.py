import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alert import Alert
from app.models.alert_date import AlertDate
from app.models.alerts import Alerts
from app.models.planned_test import PlannedTest  # noqa silence linter
from tests.conftest import create_alert_dict


def test_load(alert_dict, mocker):
    mocker.patch.object(Alerts, 'from_yaml', return_value=[alert_dict])
    mocker.patch.object(Alerts, 'from_api', return_value=[alert_dict])
    alerts = Alerts.load()
    assert len(alerts) == 2
    assert isinstance(alerts[0], Alert)


def test_load_filters_areas(tmp_path, alert_dict, mocker):
    alert_dict['areas']['simple_polygons'] = 'polygons'
    mocker.patch.object(Alerts, 'from_yaml', return_value=[alert_dict])
    mocker.patch.object(Alerts, 'from_api', return_value=[])

    mocker.patch('app.models.alerts.is_in_uk', return_value=False)
    assert len(Alerts.load()) == 0

    mocker.patch('app.models.alerts.is_in_uk', return_value=True)
    assert len(Alerts.load()) == 1


def test_from_yaml():
    assert len(Alerts.from_yaml()) > 0
    assert isinstance(Alerts.from_yaml()[0], dict)


@freeze_time('2021-04-21T11:30:00Z')
def test_last_updated(alert_dict):
    alert_dict['starts_at'] = dt_parse('2021-04-21T11:10:00Z')
    alert_dict_2 = alert_dict.copy()
    alert_dict_2['starts_at'] = dt_parse('2021-04-21T11:20:00Z')

    alerts = Alerts([alert_dict, alert_dict_2])

    assert len(alerts) == len(alerts.current_and_public) == 2
    assert isinstance(alerts.last_updated_date, AlertDate)
    assert alerts.last_updated == alert_dict_2['starts_at']


def test_last_updated_exception_for_no_current_alerts(alert_dict):
    with pytest.raises(ValueError):
        Alerts([alert_dict]).last_updated


def test_current_and_public_alerts(alert_dict, mocker):
    mocker.patch(__name__ + '.Alert.is_current_and_public', True)
    assert len(Alerts([alert_dict]).current_and_public) == 1

    mocker.patch(__name__ + '.Alert.is_current_and_public', False)
    assert len(Alerts([alert_dict]).current_and_public) == 0


def test_planned_alerts(alert_dict, planned_test_dict, mocker):
    mocker.patch(__name__ + '.PlannedTest.is_planned', False)
    assert len(Alerts([alert_dict]).planned) == 0

    mocker.patch(__name__ + '.Alert.is_planned', True)
    mocker.patch(__name__ + '.Alert.is_public', False)
    assert len(Alerts([alert_dict]).planned) == 1

    mocker.patch(__name__ + '.Alert.is_planned', True)
    mocker.patch(__name__ + '.Alert.is_public', True)
    assert len(Alerts([alert_dict]).planned) == 0

    mocker.patch(__name__ + '.PlannedTest.is_planned', False)
    mocker.patch(__name__ + '.Alert.is_planned', False)
    assert len(Alerts([alert_dict] + [planned_test_dict]).planned) == 0

    mocker.patch(__name__ + '.PlannedTest.is_planned', True)
    mocker.patch(__name__ + '.Alert.is_planned', True)
    mocker.patch(__name__ + '.Alert.is_public', False)
    assert len(Alerts([alert_dict] + [planned_test_dict]).planned) == 2


def test_expired_alerts(alert_dict, mocker):
    mocker.patch(__name__ + '.Alert.is_expired', True)
    assert len(Alerts([alert_dict]).expired) == 1

    mocker.patch(__name__ + '.Alert.is_expired', False)
    assert len(Alerts([alert_dict]).expired) == 0


def test_public_alerts(alert_dict, mocker):
    mocker.patch(__name__ + '.Alert.is_public', True)
    assert len(Alerts([alert_dict]).public) == 1

    mocker.patch(__name__ + '.Alert.is_public', False)
    assert len(Alerts([alert_dict]).public) == 0


@freeze_time('2021-01-01T00:00:00Z')
def test_public_alerts_dont_get_listed_as_tests(mocker):
    mocker.patch(__name__ + '.Alert.is_current_and_public', True)
    alerts = Alerts([
        create_alert_dict(),
        create_alert_dict(),
    ])

    assert len(alerts) == 2
    assert len(alerts.current_and_public) == 2
    assert len(alerts.test_alerts_today) == 0
    assert len(alerts.current_and_planned_test_alerts) == 0
    assert alerts.dates_of_current_and_planned_test_alerts == set()


@freeze_time('2021-01-01')
def test_multiple_test_alerts_on_the_same_day_are_aggregated(mocker):
    mocker.patch(__name__ + '.Alert.is_public', False)
    alerts = Alerts([
        create_alert_dict(
            starts_at='2021-01-01T01:01:01Z'
        ),
        create_alert_dict(
            starts_at='2021-01-01T02:02:02Z'
        ),
    ])

    assert len(alerts) == 2
    assert len(alerts.current_and_public) == 0
    assert len(alerts.test_alerts_today) == 2
    assert len(alerts.current_and_planned_test_alerts) == 2
    assert alerts.dates_of_current_and_planned_test_alerts == {
        AlertDate(dt_parse('2021-01-01T12:01:00Z'))
    }
