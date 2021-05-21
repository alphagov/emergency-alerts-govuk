from lib.alert import Alert
import pytz
import pytest

from datetime import datetime
from freezegun import freeze_time

from lib.alert_date import AlertDate


def test_init_converts_alert_sent_and_expiry_dates_to_AlertDate_class(alert_dict):
    alert = Alert(alert_dict)
    assert isinstance(alert.sent, AlertDate)
    assert isinstance(alert.expires, AlertDate)


@pytest.mark.parametrize('expiry_date,is_current', [
    [datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc), True],
    [datetime(2021, 4, 21, 9, 30, tzinfo=pytz.utc), False],
])
@freeze_time(datetime(
    2021, 4, 21, 10, 30, tzinfo=pytz.utc
))
def test_is_current_alert_checks_if_alert_is_current(expiry_date, is_current, alert_dict):
    alert_dict['expires'] = expiry_date
    assert Alert(alert_dict).is_current == is_current
