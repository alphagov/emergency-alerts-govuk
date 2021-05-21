from datetime import datetime

import pytest
import pytz
import yaml

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
