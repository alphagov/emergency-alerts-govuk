from datetime import datetime

import pytest
import pytz
from freezegun import freeze_time

from lib.alert import Alert
from lib.alert_date import AlertDate


def test_alert_timestamps_properties_are_AlertDates(alert_dict):
    alert = Alert(alert_dict)
    assert isinstance(alert.approved_at_date, AlertDate)
    assert isinstance(alert.cancelled_at_date, AlertDate)
    assert isinstance(alert.finishes_at_date, AlertDate)
    assert isinstance(alert.starts_at_date, AlertDate)


def test_expires_date_returns_earliest_expiry_time(alert_dict):
    alert = Alert(alert_dict)
    assert alert.expires_date.as_iso8601 == alert.cancelled_at_date.as_iso8601

    alert_dict['cancelled_at'] = None
    alert = Alert(alert_dict)
    assert alert.expires_date.as_iso8601 == alert.finishes_at_date.as_iso8601


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
    alert_dict['cancelled_at'] = expiry_date
    assert Alert(alert_dict).is_expired == is_expired


@pytest.mark.parametrize('approved_at_date,expiry_date,is_current', [
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
    approved_at_date,
    expiry_date,
    is_current,
    alert_dict
):
    alert_dict['approved_at'] = approved_at_date
    alert_dict['cancelled_at'] = expiry_date
    assert Alert(alert_dict).is_current == is_current


@pytest.mark.parametrize('is_current,is_public,is_current_and_public', [
    [True, True, True],
    [False, True, False],
    [True, False, False],
    [False, False, False]
])
def test_is_current_and_public(is_current, is_public, is_current_and_public, mocker, alert_dict):
    mocker.patch(__name__ + '.Alert.is_current', is_current)
    mocker.patch(__name__ + '.Alert.is_public', is_public)
    assert Alert(alert_dict).is_current_and_public == is_current_and_public


@pytest.mark.parametrize('channel,is_public', [
    ['severe', True],
    ['government', True],
    ['operator', False]
])
def test_is_public(channel, is_public, alert_dict):
    alert_dict['channel'] = channel
    assert Alert(alert_dict).is_public == is_public
