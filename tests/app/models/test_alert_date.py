from datetime import datetime

import pytest
import pytz
from pytz import timezone

from app.models.alert_date import AlertDate


def test_AlertDate_properties():
    sample_datetime = datetime(2021, 3, 21, 10, 30, tzinfo=pytz.utc)
    alerts_date = AlertDate(sample_datetime)
    assert alerts_date.as_lang == 'at 10:30am on Sunday 21 March 2021'
    assert alerts_date.as_iso8601 == '2021-03-21T10:30:00+00:00'
    assert alerts_date.as_utc_datetime == sample_datetime
    assert alerts_date.as_local_datetime == sample_datetime


def test_AlertDate_properties_work_with_bst():
    sample_datetime = datetime(2021, 4, 21, 10, 30, tzinfo=pytz.utc)
    datetime_in_bst = sample_datetime.astimezone(timezone('Europe/London'))
    alerts_date = AlertDate(datetime_in_bst)
    assert alerts_date.as_lang == 'at 11:30am on Wednesday 21 April 2021'
    assert alerts_date.as_iso8601 == '2021-04-21T11:30:00+01:00'
    assert alerts_date.as_utc_datetime == sample_datetime
    assert alerts_date.as_local_datetime == datetime_in_bst


@pytest.mark.parametrize('hour, minute, expected_lang', (
    (0, 0, 'at midnight on Sunday 21 March 2021'),
    (12, 0, 'at midday on Sunday 21 March 2021'),
    (23, 59, 'at 11:59pm on Sunday 21 March 2021'),  # 12 hour clock
))
def test_AlertDate_at_midday_and_midnight(hour, minute, expected_lang):
    sample_datetime = datetime(2021, 3, 21, hour, minute, tzinfo=pytz.utc)
    alerts_date = AlertDate(sample_datetime)
    assert alerts_date.as_lang == expected_lang
