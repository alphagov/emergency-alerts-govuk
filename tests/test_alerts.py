from datetime import datetime

import pytest
import pytz
import yaml
from freezegun import freeze_time

from lib.alert import Alert
from lib.alert_date import AlertDate
from lib.alerts import Alerts


def test_from_yaml_loads_data(tmp_path, alert_dict):
    sample_yaml = yaml.dump({
        'last_updated': datetime(2020, 1, 1, 10, 00),
        'alerts': [alert_dict]
    })

    data_file = tmp_path / 'data.yaml'
    data_file.write_text(sample_yaml)

    alerts = Alerts.from_yaml(data_file)
    assert len(alerts) == 1
    assert isinstance(alerts[0], Alert)
    assert isinstance(alerts.last_updated_date, AlertDate)


@pytest.mark.parametrize('sent_date,expiry_date,expected_len', [
    [
        datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc),
        datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        1
    ],
    [
        datetime(2021, 4, 21, 11, 0, tzinfo=pytz.utc),
        datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        0
    ],
    [
        datetime(2021, 4, 21, 9, 0, tzinfo=pytz.utc),
        datetime(2021, 4, 21, 10, 0, tzinfo=pytz.utc),
        0
    ],
])
@freeze_time(datetime(
    2021, 4, 21, 10, 30, tzinfo=pytz.utc
))
def test_current_alerts_are_current(sent_date, expiry_date, expected_len, alert_dict):
    alert_dict['sent'] = sent_date
    alert_dict['expires'] = expiry_date

    alerts = Alerts({
        'last_updated': datetime(2020, 1, 1, 10, 00),
        'alerts': [alert_dict]
    })

    assert len(alerts.current) == expected_len
