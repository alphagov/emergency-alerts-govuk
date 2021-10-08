from datetime import datetime

import pytest
from freezegun import freeze_time

from app.models.alert import Alert
from app.models.alert_date import AlertDate
from app.models.alerts import Alerts


def test_load_includes_yaml_data(alert_dict, mocker):
    mocker.patch.object(Alerts, 'from_yaml', return_value=[alert_dict])
    alerts = Alerts.load()
    assert len(alerts) == 1
    assert isinstance(alerts[0], Alert)


def test_load_filters_areas(tmp_path, alert_dict, mocker):
    alert_dict['areas']['simple_polygons'] = 'polygons'
    mocker.patch.object(Alerts, 'from_yaml', return_value=[alert_dict])

    mocker.patch('app.models.alerts.is_in_uk', return_value=False)
    assert len(Alerts.load()) == 0

    mocker.patch('app.models.alerts.is_in_uk', return_value=True)
    assert len(Alerts.load()) == 1


def test_from_yaml():
    assert len(Alerts.from_yaml()) > 0
    assert isinstance(Alerts.from_yaml()[0], dict)


@freeze_time(datetime(
    2021, 4, 21, 11, 30
))
def test_last_updated(alert_dict):
    alert_dict['starts_at'] = datetime(
        2021, 4, 21, 11, 10
    )
    alert_dict_2 = alert_dict.copy()
    alert_dict_2['starts_at'] = datetime(
        2021, 4, 21, 11, 20
    )

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
