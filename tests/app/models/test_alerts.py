from datetime import datetime

import pytest
import yaml
from freezegun import freeze_time

from app.models.alert import Alert
from app.models.alert_date import AlertDate
from app.models.alerts import Alerts


@freeze_time(datetime(
    2021, 4, 21, 11, 30
))
def test_from_yaml_loads_data(tmp_path, alert_dict):
    sample_yaml = yaml.dump({
        'alerts': [alert_dict],
    })

    data_file = tmp_path / 'data.yaml'
    data_file.write_text(sample_yaml)

    alerts = Alerts.from_yaml(data_file)
    assert len(alerts) == 1
    assert isinstance(alerts[0], Alert)
    assert isinstance(alerts.last_updated_date, AlertDate)


def test_from_yaml_filters_areas(tmp_path, alert_dict, mocker):
    alert_dict['areas']['simple_polygons'] = 'polygons'
    sample_yaml = yaml.dump({'alerts': [alert_dict]})

    data_file = tmp_path / 'data.yaml'
    data_file.write_text(sample_yaml)

    mocker.patch('app.models.alerts.is_in_uk', return_value=False)
    assert len(Alerts.from_yaml(data_file)) == 0

    mocker.patch('app.models.alerts.is_in_uk', return_value=True)
    assert len(Alerts.from_yaml(data_file)) == 1


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
