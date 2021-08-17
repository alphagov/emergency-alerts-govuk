from datetime import datetime

import pytest
import pytz

from app.models.alerts import Alerts
from app.utils import REPO


@pytest.fixture()
def alerts():
    return Alerts.from_yaml(REPO / 'data.yaml')


def test_alert_sent_before_starts_before_expires(alerts):
    for alert in alerts:
        assert alert.approved_at_date.as_utc_datetime <= alert.starts_at_date.as_utc_datetime
        assert alert.starts_at_date.as_utc_datetime < alert.expires_date.as_utc_datetime


def test_alert_cancelled_before_finishes(alerts):
    for alert in alerts:
        if alert.cancelled_at:
            assert alert.cancelled_at_date.as_utc_datetime <= alert.finishes_at_date.as_utc_datetime


def is_date_in_london_timezone_including_summertime(date):
    if not isinstance(date, datetime):
        return False
    zoneless_date = date.replace(tzinfo=None)
    date_with_expected_offset = pytz.timezone('Europe/London').localize(zoneless_date)
    return date_with_expected_offset.utcoffset() == date.utcoffset()


def test_dates_in_alerts_data_include_explicit_timezone_offset(alerts):
    for alert in alerts:
        assert is_date_in_london_timezone_including_summertime(alert.approved_at)
        assert is_date_in_london_timezone_including_summertime(alert.starts_at)
        assert is_date_in_london_timezone_including_summertime(alert.finishes_at)

        if alert.cancelled_at:
            assert is_date_in_london_timezone_including_summertime(alert.cancelled_at)
