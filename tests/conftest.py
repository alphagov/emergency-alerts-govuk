from datetime import datetime

import pytest
import pytz


@pytest.fixture()
def alert_dict():
    return {
        'headline': 'Emergency alert',
        'description': 'Something',
        'area_names': [],
        'message_type': 'alert',
        'identifier': '1234',
        'sent': datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        'expires': datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc)
    }
