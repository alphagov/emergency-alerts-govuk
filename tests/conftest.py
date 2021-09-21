import uuid
from datetime import datetime

import pytest
import pytz
from bs4 import BeautifulSoup

from app import create_app
from app.models.alerts import Alerts


@pytest.fixture()
def alert_dict():
    return {
        'id': str(uuid.UUID(int=0)),
        'headline': 'Emergency alert',
        'content': 'Something',
        'areas': dict(),
        'channel': 'severe',
        'identifier': '1234',
        'starts_at': datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        'approved_at': datetime(2021, 4, 21, 11, 25, tzinfo=pytz.utc),
        'cancelled_at': datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc),
        'finishes_at': datetime(2021, 4, 21, 15, 30, tzinfo=pytz.utc)
    }


@pytest.fixture(scope='session')
def govuk_alerts():
    app = create_app()

    ctx = app.app_context()
    ctx.push()

    yield app
    ctx.pop()


@pytest.fixture()
def client_get(govuk_alerts, mocker):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([]))
    mocker.patch('app.render.file_fingerprint', return_value='1234')

    def _do_get(path):
        with govuk_alerts.test_client() as client:
            response = client.get(path)
            html_text = response.data.decode('utf-8')
            return BeautifulSoup(html_text, 'html.parser')

    return _do_get
