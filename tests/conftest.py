import pytz
from datetime import datetime
import pytest


@pytest.fixture()
def alert_dict():
    return {
        'sent': datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        'expires': datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc)
    }
