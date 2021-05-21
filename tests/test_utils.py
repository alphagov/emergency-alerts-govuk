import pytest
import pytz

from datetime import datetime
from freezegun import freeze_time
from lib.utils import file_fingerprint, is_current_alert
from lib.alert import Alert
from pathlib import Path


def test_file_fingerprint_adds_hash_to_file_path():
    new_path = file_fingerprint('/tests/test_files/example.txt', root=Path('.'))
    assert new_path == '/tests/test_files/example.txt?4d93d51945b88325c213640ef59fc50b'


@pytest.mark.parametrize('expiry_date,is_current', [
    [datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc), True],
    [datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc), False],
])
@freeze_time(datetime(
    2021, 4, 21, 10, 30, tzinfo=pytz.utc
))
def test_is_current_alert_checks_if_alert_is_current(expiry_date, is_current, alert_dict):
    alert_dict['expires'] = expiry_date
    assert is_current_alert(Alert(alert_dict)) == is_current
