import uuid

import pytest
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from app import create_app
from app.models.alerts import Alerts


def create_alert_dict(
    *,
    id=None,
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
        'content': content or 'Something',
        'areas': areas or dict(),
        'channel': channel or 'severe',
        'starts_at': starts_at or dt_parse('2021-04-21T11:30:00Z'),
        'approved_at': approved_at or dt_parse('2021-04-21T11:25:00Z'),
        'cancelled_at': cancelled_at if cancelled_at != -1 else dt_parse('2021-04-21T12:30:00Z'),
        'finishes_at': finishes_at or dt_parse('2021-04-21T15:30:00Z'),
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
