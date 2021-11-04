import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alert import Alert, PlannedTest
from app.models.alert_date import AlertDate
from tests.conftest import create_alert_dict, create_planned_test_dict


def test_alert_timestamps_properties_are_AlertDates(alert_dict):
    alert = Alert(alert_dict)
    assert isinstance(alert.approved_at_date, AlertDate)
    assert isinstance(alert.cancelled_at_date, AlertDate)
    assert isinstance(alert.finishes_at_date, AlertDate)
    assert isinstance(alert.starts_at_date, AlertDate)


def test_planned_test_timestamps_properties_are_AlertDates(planned_test_dict):
    planned_test = PlannedTest(planned_test_dict)
    assert isinstance(planned_test.starts_at_date, AlertDate)
    assert not hasattr(planned_test, 'approved_at_date')
    assert not hasattr(planned_test, 'cancelled_at_date')
    assert not hasattr(planned_test, 'finishes_at_date')


@pytest.mark.parametrize('model, fixture', (
    (Alert, create_alert_dict),
    (PlannedTest, create_planned_test_dict),
))
def test_lt_compares_alerts_based_on_start_date(model, fixture):
    alert_dict_1 = fixture()
    alert_dict_2 = fixture()

    alert_dict_1['starts_at'] = dt_parse('2021-04-21T11:30:00Z')
    alert_dict_2['starts_at'] = dt_parse('2021-04-21T12:30:00Z')

    assert model(alert_dict_1) < model(alert_dict_2)


def test_display_areas_falls_back_to_granular_names(alert_dict):
    alert_dict['areas']['aggregate_names'] = ['aggregate name']
    alert_dict['areas']['names'] = ['granular name']

    assert Alert(alert_dict).display_areas == ['aggregate name']

    del alert_dict['areas']['aggregate_names']
    assert Alert(alert_dict).display_areas == ['granular name']

    del alert_dict['areas']['names']
    assert Alert(alert_dict).display_areas == []


def test_planned_test_only_has_display_areas():
    assert PlannedTest(
        create_planned_test_dict()
    ).display_areas == []

    assert PlannedTest(
        create_planned_test_dict(display_areas=['a', 'b'])
    ).display_areas == ['a', 'b']

    assert not hasattr(
        PlannedTest(create_planned_test_dict()),
        'areas',
    )


def test_expires_date_returns_earliest_expiry_time(alert_dict):
    alert = Alert(alert_dict)
    assert alert.expires_date.as_iso8601 == alert.cancelled_at_date.as_iso8601

    alert_dict['cancelled_at'] = None
    alert = Alert(alert_dict)
    assert alert.expires_date.as_iso8601 == alert.finishes_at_date.as_iso8601


@pytest.mark.parametrize('expiry_date,is_expired', [
    [dt_parse('2021-04-21T09:30:00Z'), True],
    [dt_parse('2021-04-21T11:00:00Z'), False],
])
@freeze_time('2021-04-21T10:30:00Z')
def test_is_expired_alert_checks_if_alert_is_expired(
    expiry_date,
    is_expired,
    alert_dict
):
    alert_dict['cancelled_at'] = expiry_date
    assert Alert(alert_dict).is_expired == is_expired


@pytest.mark.parametrize('approved_at_date,expiry_date,is_current', [
    [
        dt_parse('2021-04-21T09:30:00Z'),
        dt_parse('2021-04-21T11:30:00Z'),
        True
    ],
    [
        dt_parse('2021-04-21T11:00:00Z'),
        dt_parse('2021-04-21T11:30:00Z'),
        False
    ],
    [
        dt_parse('2021-04-21T09:00:00Z'),
        dt_parse('2021-04-21T10:00:00Z'),
        False
    ],
])
@freeze_time('2021-04-21T10:30:00Z')
def test_is_current_alert_checks_if_alert_is_current(
    approved_at_date,
    expiry_date,
    is_current,
    alert_dict
):
    alert_dict['approved_at'] = approved_at_date
    alert_dict['cancelled_at'] = expiry_date
    assert Alert(alert_dict).is_current == is_current


@pytest.mark.parametrize('is_current,is_public,is_current_and_public', [
    [True, True, True],
    [False, True, False],
    [True, False, False],
    [False, False, False]
])
def test_is_current_and_public(is_current, is_public, is_current_and_public, mocker, alert_dict):
    mocker.patch(__name__ + '.Alert.is_current', is_current)
    mocker.patch(__name__ + '.Alert.is_public', is_public)
    assert Alert(alert_dict).is_current_and_public == is_current_and_public


@pytest.mark.parametrize('channel,is_public', [
    ['severe', True],
    ['government', True],
    ['operator', False],
    ['test', False]
])
def test_is_public(channel, is_public, alert_dict):
    alert_dict['channel'] = channel
    assert Alert(alert_dict).is_public == is_public


@pytest.mark.parametrize('channel, expected_display_areas', [
    ('severe', ['Chipping Sodbury']),
    ('government', ['Chipping Sodbury']),
    ('operator', []),
    ('test', [])
])
def test_displayed_areas_for_public_alerts_only(
    channel, expected_display_areas, alert_dict
):
    alert_dict['channel'] = channel
    alert_dict['areas']['aggregate_names'] = ['Chipping Sodbury']
    assert Alert(alert_dict).display_areas == expected_display_areas
