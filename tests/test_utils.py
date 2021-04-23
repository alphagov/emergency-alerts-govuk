import pytest

from datetime import datetime, timezone
from freezegun import freeze_time
from lib.utils import AlertsDate, convert_dates, file_fingerprint, is_current_alert
from pathlib import Path


def test_AlertsDate_properties():
    _datetime = datetime(2021, 4, 21, 10, 30)
    alerts_date = AlertsDate(_datetime)
    assert alerts_date.as_lang == '21 April 2021 at 10:30'
    assert alerts_date.as_iso8601 == '2021-04-21T10:30:00'
    assert alerts_date.as_datetime == _datetime


def test_file_fingerprint_adds_hash_to_file_path():
    new_path = file_fingerprint('/tests/test_files/example.txt', root=Path('.'))
    assert new_path == '/tests/test_files/example.txt?4d93d51945b88325c213640ef59fc50b'


@pytest.mark.parametrize('expiry_date,message_type,is_current', [
    [datetime(2021, 4, 21, 11, 30, tzinfo=timezone.utc), 'alert', True],
    [datetime(2021, 4, 21, 9, 30, tzinfo=timezone.utc), 'alert', False],
    [datetime(2021, 4, 21, 11, 30, tzinfo=timezone.utc), 'cancel', False]
])
@freeze_time(datetime(
    2021, 4, 21, 10, 30, tzinfo=timezone.utc
))
def test_is_current_alert_checks_if_alert_is_current(expiry_date, message_type, is_current):
    alert = {
        'message_type': message_type,
        'expires': expiry_date
    }
    assert is_current_alert(alert) == is_current


def test_convert_dates_converts_alert_sent_and_expiry_dates_to_AlertsDate_class():
    alert = {
        'message_type': 'alert',
        'expires': datetime(2021, 4, 21, 9, 30, tzinfo=timezone.utc),
        'sent': datetime(2021, 4, 20, 9, 30, tzinfo=timezone.utc),
    }
    assert not isinstance(alert['sent'], AlertsDate)
    assert not isinstance(alert['expires'], AlertsDate)

    converted_alert = convert_dates(alert)

    assert isinstance(converted_alert['sent'], AlertsDate)
    assert isinstance(converted_alert['expires'], AlertsDate)
