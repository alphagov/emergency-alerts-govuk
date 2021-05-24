import pytest

from lib.alerts import Alerts
from lib.utils import REPO


@pytest.fixture()
def alerts():
    return Alerts.from_yaml(REPO / 'data.yaml')


def test_alert_sent_before_starts_before_expires(alerts):
    for alert in alerts:
        assert alert.sent_date.as_utc_datetime <= alert.starts_date.as_utc_datetime
        assert alert.starts_date.as_utc_datetime < alert.expires_date.as_utc_datetime
