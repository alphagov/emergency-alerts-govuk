import pytest
import pytz

from datetime import datetime
from freezegun import freeze_time
from lib.utils import convert_dates, file_fingerprint, is_current_alert
from lib.alert_date import AlertDate
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
def test_is_current_alert_checks_if_alert_is_current(expiry_date, is_current):
    alert = {'expires': expiry_date}
    assert is_current_alert(alert) == is_current


def test_convert_dates_converts_alert_sent_and_expiry_dates_to_AlertDate_class():
    alert = {
        'message_type': 'alert',
        'expires': datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc),
        'sent': datetime(2021, 4, 20, 9, 30, tzinfo=pytz.utc),
    }
    converted_alert = convert_dates(alert)

    assert isinstance(converted_alert['sent'], AlertDate)
    assert isinstance(converted_alert['expires'], AlertDate)
