from lib.alert import Alert
import pytz

from datetime import datetime
from lib.alert_date import AlertDate


def test_init_converts_alert_sent_and_expiry_dates_to_AlertDate_class(alert_dict):
    alert = Alert(alert_dict)
    assert isinstance(alert.sent, AlertDate)
    assert isinstance(alert.expires, AlertDate)
