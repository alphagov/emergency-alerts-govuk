from datetime import datetime
from lib.utils import AlertsDate


def test_AlertsDate_properties():
    _datetime = datetime(2021, 4, 21, 10, 30)
    alerts_date = AlertsDate(_datetime)
    assert alerts_date.as_lang == '21 April 2021 at 10:30'
    assert alerts_date.as_iso8601 == '2021-04-21T10:30:00'
    assert alerts_date.as_datetime == _datetime
