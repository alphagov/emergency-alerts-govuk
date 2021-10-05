import random
from datetime import datetime
from uuid import UUID

import pytest

from app.models.alert import Alert
from app.models.alerts import Alerts
from app.render import get_url_for_alert
from tests.conftest import create_alert_dict


def test_get_url_for_alert_doesnt_return_non_public_alerts():
    alerts = Alerts([
        create_alert_dict(
            channel='operator',
            starts_at=datetime(2021, 4, 21, 11, 30),
        )
    ])

    with pytest.raises(ValueError):
        get_url_for_alert(alerts[0], alerts)


@pytest.mark.parametrize('index, expected_url', [
    (0, '20-apr-2021'),
    (1, '21-apr-2021'),
    (2, '21-apr-2021-2'),
    (3, '21-apr-2021-3'),
    (4, '22-apr-2021'),
])
def test_get_url_for_alert_returns_url_with_count_for_alerts_on_same_day(index, expected_url):
    the_days_alerts = [
        create_alert_dict(id=UUID(int=0), starts_at=datetime(2021, 4, 20, 22, 59)),
        create_alert_dict(id=UUID(int=1), starts_at=datetime(2021, 4, 20, 23, 00)),
        create_alert_dict(id=UUID(int=2), starts_at=datetime(2021, 4, 21, 12, 31)),
        create_alert_dict(id=UUID(int=3), starts_at=datetime(2021, 4, 21, 12, 31)),
        create_alert_dict(id=UUID(int=4), starts_at=datetime(2021, 4, 21, 23, 00)),
    ]

    alerts = Alerts(the_days_alerts)

    assert get_url_for_alert(Alert(the_days_alerts[index]), alerts) == expected_url


def test_get_url_for_alert_consistently_sorts_by_id():
    # all have the same start time
    the_days_alerts = [
        create_alert_dict(id=UUID(int=0)),
        create_alert_dict(id=UUID(int=1)),
        create_alert_dict(id=UUID(int=2)),
        create_alert_dict(id=UUID(int=3)),
        create_alert_dict(id=UUID(int=4)),
        create_alert_dict(id=UUID(int=5)),
        create_alert_dict(id=UUID(int=6)),
    ]

    # shuffle to make sure the order that alerts go in doesn't affect anything
    alerts = Alerts(random.sample(the_days_alerts, len(the_days_alerts)))

    assert get_url_for_alert(Alert(the_days_alerts[0]), alerts) == '21-apr-2021'
    assert get_url_for_alert(Alert(the_days_alerts[3]), alerts) == '21-apr-2021-4'
    assert get_url_for_alert(Alert(the_days_alerts[6]), alerts) == '21-apr-2021-7'


def test_get_url_for_alert_skips_non_public_alerts():
    the_days_alerts = [
        create_alert_dict(starts_at=datetime(2021, 4, 21, 12, 00), channel='operator'),
        create_alert_dict(starts_at=datetime(2021, 4, 21, 13, 00), channel='severe'),
    ]

    alerts = Alerts(the_days_alerts)

    # doesn't have the -2 suffix as we skip the operator alert
    assert get_url_for_alert(Alert(the_days_alerts[1]), alerts) == '21-apr-2021'
