import pytest

from app.models.alerts import Alerts


@pytest.fixture()
def alerts():
    return Alerts.from_yaml()


def test_alert_sent_before_starts_before_expires(alerts):
    for alert in alerts:
        assert alert.approved_at_date.as_utc_datetime <= alert.starts_at_date.as_utc_datetime
        assert alert.starts_at_date.as_utc_datetime < alert.expires_date.as_utc_datetime


def test_alert_cancelled_before_finishes(alerts):
    for alert in alerts:
        if alert.cancelled_at:
            assert alert.cancelled_at_date.as_utc_datetime <= alert.finishes_at_date.as_utc_datetime
