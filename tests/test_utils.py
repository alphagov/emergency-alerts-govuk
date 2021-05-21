import pytest
import pytz

from datetime import datetime
from freezegun import freeze_time
from lib.utils import AlertsDate, convert_dates, file_fingerprint, is_current_alert
from pathlib import Path
from pytz import timezone


def test_AlertsDate_properties():
    sample_datetime = datetime(2021, 3, 21, 10, 30, tzinfo=pytz.utc)
    alerts_date = AlertsDate(sample_datetime)
    assert alerts_date.as_lang == '21 March 2021 at 10:30'
    assert alerts_date.as_iso8601 == '2021-03-21T10:30:00+00:00'
    assert alerts_date.as_datetime == sample_datetime
    assert alerts_date.as_local_datetime == sample_datetime  # sample date is outside of British Summer Time (BST)


def test_AlertsDate_properties_work_with_bst():
    datetime_in_bst = datetime(2021, 4, 21, 10, 30, tzinfo=pytz.utc)
    alerts_date = AlertsDate(datetime_in_bst)
    assert alerts_date.as_lang == '21 April 2021 at 11:30'
    assert alerts_date.as_iso8601 == '2021-04-21T11:30:00+01:00'
    assert alerts_date.as_datetime == datetime_in_bst.astimezone(timezone('Europe/London'))


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


def test_convert_dates_converts_alert_sent_and_expiry_dates_to_AlertsDate_class():
    alert = {
        'message_type': 'alert',
        'expires': datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc),
        'sent': datetime(2021, 4, 20, 9, 30, tzinfo=pytz.utc),
    }
    converted_alert = convert_dates(alert)

    assert isinstance(converted_alert['sent'], AlertsDate)
    assert isinstance(converted_alert['expires'], AlertsDate)
