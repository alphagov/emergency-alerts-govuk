from datetime import datetime

import pytest
import pytz
from freezegun import freeze_time

from lib.alert import Alert
from lib.alert_date import AlertDate


def test_alert_timestamps_properties_are_AlertDates(alert_dict):
    alert = Alert(alert_dict)
    assert isinstance(alert.sent_date, AlertDate)
    assert isinstance(alert.expires_date, AlertDate)
    assert isinstance(alert.starts_date, AlertDate)


@pytest.mark.parametrize('expiry_date,is_expired', [
    [datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc), True],
    [datetime(2021, 4, 21, 11, 0, tzinfo=pytz.utc), False],
])
@freeze_time(datetime(
    2021, 4, 21, 10, 30, tzinfo=pytz.utc
))
def test_is_expired_alert_checks_if_alert_is_expired(
    expiry_date,
    is_expired,
    alert_dict
):
    alert_dict['expires'] = expiry_date
    assert Alert(alert_dict).is_expired == is_expired


@pytest.mark.parametrize('starts_date,expiry_date,is_current', [
    [
        datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc),
        datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        True
    ],
    [
        datetime(2021, 4, 21, 11, 0, tzinfo=pytz.utc),
        datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        False
    ],
    [
        datetime(2021, 4, 21, 9, 0, tzinfo=pytz.utc),
        datetime(2021, 4, 21, 10, 0, tzinfo=pytz.utc),
        False
    ],
])
@freeze_time(datetime(
    2021, 4, 21, 10, 30, tzinfo=pytz.utc
))
def test_is_current_alert_checks_if_alert_is_current(
    starts_date,
    expiry_date,
    is_current,
    alert_dict
):
    alert_dict['starts'] = starts_date
    alert_dict['expires'] = expiry_date
    assert Alert(alert_dict).is_current == is_current
