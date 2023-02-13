from datetime import date

import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alert_date import AlertDate


def test_AlertDate_properties():
    sample_datetime = dt_parse('2021-03-02T10:30:00Z')
    alerts_date = AlertDate(sample_datetime)
    assert alerts_date.as_lang == 'at 10:30am on Tuesday 2 March 2021'
    assert alerts_date.as_alert_lang == 'Tuesday 2 March 2021, at 10AM'
    assert alerts_date.as_iso8601 == '2021-03-02T10:30:00+00:00'
    assert alerts_date.as_utc_datetime == dt_parse('2021-03-02T10:30:00Z')
    assert alerts_date.as_local_datetime == dt_parse('2021-03-02T10:30:00Z')
    assert alerts_date.as_url == '2-mar-2021'


def test_AlertDate_properties_work_with_bst():
    sample_datetime = dt_parse('2021-04-20T23:30:00Z')
    alerts_date = AlertDate(sample_datetime)
    assert alerts_date.as_lang == 'at 12:30am on Wednesday 21 April 2021'
    assert alerts_date.as_alert_lang == 'Wednesday 21 April 2021, at 12AM'
    assert alerts_date.as_iso8601 == '2021-04-21T00:30:00+01:00'
    assert alerts_date.as_utc_datetime == dt_parse('2021-04-20T23:30:00Z')
    assert alerts_date.as_local_datetime == dt_parse('2021-04-21T00:30:00+01:00')
    assert alerts_date.as_local_date == date(2021, 4, 21)
    assert alerts_date.as_url == '21-apr-2021'


@pytest.mark.parametrize('hour, minute, expected_lang', (
    ('00', '00', 'at midnight on Sunday 21 March 2021'),
    ('12', '00', 'at midday on Sunday 21 March 2021'),
    ('23', '59', 'at 11:59pm on Sunday 21 March 2021'),  # 12 hour clock
))
def test_AlertDate_at_midday_and_midnight(hour, minute, expected_lang):
    sample_datetime = dt_parse(f'2021-03-21T{hour}:{minute}:00Z')
    alerts_date = AlertDate(sample_datetime)
    assert alerts_date.as_lang == expected_lang


@pytest.mark.parametrize('now, sample, expected_is_today', (
    # GMT
    ('2021-01-01T00:00:00Z', '2021-12-31T23:59:59Z', False),
    ('2021-01-01T00:00:00Z', '2021-01-01T00:00:00Z', True),
    ('2021-01-01T23:59:59Z', '2021-01-01T00:00:00Z', True),
    ('2021-01-01T00:00:00Z', '2021-01-01T23:59:59Z', True),
    ('2021-01-01T23:59:59Z', '2021-01-01T23:59:59Z', True),
    ('2021-01-01T23:59:59Z', '2021-01-02T00:00:00Z', False),
    # BST
    ('2021-05-31T23:00:00Z', '2021-05-31T22:59:59Z', False),
    ('2021-05-31T23:00:00Z', '2021-05-31T23:00:00Z', True),
    ('2021-06-01T22:59:59Z', '2021-05-31T23:00:00Z', True),
    ('2021-05-31T23:00:00Z', '2021-06-01T22:59:59Z', True),
    ('2021-06-01T22:59:59Z', '2021-06-01T22:59:59Z', True),
    ('2021-06-01T22:59:59Z', '2021-06-01T23:00:00Z', False),
))
def test_AlertDate_is_today(now, sample, expected_is_today):
    with freeze_time(now):
        assert AlertDate(dt_parse(sample)).is_today == expected_is_today
