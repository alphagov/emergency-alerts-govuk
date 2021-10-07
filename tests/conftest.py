import uuid
from datetime import datetime

import pytest
from bs4 import BeautifulSoup

from app import create_app
from app.models.alerts import Alerts


def create_alert_dict(
    *,
    id=None,
    headline=None,
    content=None,
    areas=None,
    channel=None,
    starts_at=None,
    approved_at=None,
    # -1 is a sentinel value, so None can be passed in
    cancelled_at=-1,
    finishes_at=None,
):
    return {
        'id': str(id or uuid.UUID(int=0)),
        'headline': headline or 'Emergency alert',
        'content': content or 'Something',
        'areas': areas or dict(),
        'channel': channel or 'severe',
        'starts_at': starts_at or datetime(2021, 4, 21, 11, 30),
        'approved_at': approved_at or datetime(2021, 4, 21, 11, 25),
        'cancelled_at': cancelled_at if cancelled_at != -1 else datetime(2021, 4, 21, 12, 30),
        'finishes_at': finishes_at or datetime(2021, 4, 21, 15, 30)
    }


@pytest.fixture()
def alert_dict():
    return create_alert_dict()


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
            assert response.status_code == 200, f'{path} returned {response.status_code}'
            html_text = response.data.decode('utf-8')
            return BeautifulSoup(html_text, 'html.parser')

    return _do_get
