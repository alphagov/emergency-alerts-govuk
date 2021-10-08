from datetime import timedelta

import pytest

from app.models.alert import Alert
from app.models.alerts import Alerts

TIMESTAMP_FIELDS = [
    'approved_at',
    'starts_at',
    'finishes_at',
    'cancelled_at'
]


@pytest.fixture()
def alerts():
    return [Alert(alert_dict) for alert_dict in Alerts.from_yaml()]


def test_alert_timestamps_in_utc(alerts):
    for alert_dict in Alerts.from_yaml():
        for field in TIMESTAMP_FIELDS:
            if alert_dict[field]:
                assert alert_dict[field].utcoffset() == timedelta(0)


def test_alert_sent_before_starts_before_expires(alerts):
    for alert in alerts:
        assert alert.approved_at_date.as_utc_datetime <= alert.starts_at_date.as_utc_datetime
        assert alert.starts_at_date.as_utc_datetime < alert.expires_date.as_utc_datetime


def test_alert_cancelled_before_finishes(alerts):
    for alert in alerts:
        if alert.cancelled_at:
            assert alert.cancelled_at_date.as_utc_datetime <= alert.finishes_at_date.as_utc_datetime
