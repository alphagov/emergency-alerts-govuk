from datetime import datetime
from lib.utils import AlertsDate, file_fingerprint
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
