import uuid

import pytest
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from app import create_app
from app.models.alerts import Alerts
from app.models.planned_tests import PlannedTests


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
    extra_content=None,
    starts_at_date=None
):
    return {
        'id': str(id or uuid.UUID(int=0)),
        'content': content or 'Something',
        'areas': areas or {"aggregate_names": ['England']},
        'channel': channel or 'severe',
        'starts_at': starts_at or dt_parse('2021-04-21T11:30:00Z'),
        'approved_at': approved_at or dt_parse('2021-04-21T11:25:00Z'),
        'cancelled_at': cancelled_at if cancelled_at != -1 else dt_parse('2021-04-21T12:30:00Z'),
        'finishes_at': finishes_at or dt_parse('2021-04-21T15:30:00Z'),
        'extra_content': extra_content,
        "starts_at_date": starts_at_date or dt_parse('2021-04-21T11:30:00Z')
    }


def create_planned_test_dict(
    id=None,
    channel=None,
    approved_at=None,
    starts_at=None,
    cancelled_at=None,
    finishes_at=None,
    display_in_status_box=None,
    status_box_content=None,
    welsh_status_box_content=None,
    summary=None,
    welsh_summary=None,
    content=None,
    welsh_content=None,
    areas=None,
    extra_content=None,
    starts_at_datetime_in_welsh=None,
    areas_in_welsh=None
):
    return {
        'id': id or uuid.uuid4(),
        'channel': channel or 'operator',
        'approved_at': approved_at or dt_parse('2021-04-16T12:00:00Z'),
        'starts_at': starts_at or dt_parse('2021-04-21T11:30:00Z'),
        'cancelled_at': cancelled_at or None,
        'finishes_at': finishes_at or dt_parse('2021-04-21T13:30:00Z'),
        'areas': areas or [],
        'display_in_status_box': display_in_status_box,
        'status_box_content': status_box_content,
        'welsh_status_box_content': welsh_status_box_content,
        'summary': summary,
        'welsh_summary': welsh_summary,
        'content': content,
        'welsh_content': welsh_content,
        "extra_content": None,
        'display_as_link': True,
        'areas_in_welsh': areas_in_welsh or [],
        'starts_at_datetime_in_welsh': starts_at_datetime_in_welsh or None
    }


@pytest.fixture()
def alert_dict():
    return create_alert_dict()


@pytest.fixture()
def planned_test_dict():
    return create_planned_test_dict()


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
    mocker.patch('app.models.planned_tests.PlannedTests.from_yaml', return_value=PlannedTests([]))
    mocker.patch('app.render.file_fingerprint', return_value='1234')

    def _do_get(path):
        with govuk_alerts.test_client() as client:
            response = client.get(path)
            assert response.status_code == 200, f'{path} returned {response.status_code}'
            html_text = response.data.decode('utf-8')
            return BeautifulSoup(html_text, 'html.parser')

    return _do_get


@pytest.fixture()
def sample_content():
    return """This is a mobile network operator test of the Emergency Alerts service.
    You do not need to take any action. To find out more, search for gov.uk/alerts"""
