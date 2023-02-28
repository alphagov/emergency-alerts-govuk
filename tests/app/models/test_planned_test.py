from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alert_date import AlertDate
from app.models.planned_test import PlannedTest
from tests.conftest import create_planned_test_dict


def test_planned_test_timestamps_properties_are_AlertDates(planned_test_dict):
    planned_test = PlannedTest(planned_test_dict)
    assert isinstance(planned_test.starts_at_date, AlertDate)


def test_lt_compares_planned_tests_based_on_start_date():
    alert_dict_1 = create_planned_test_dict()
    alert_dict_2 = create_planned_test_dict()

    alert_dict_1['starts_at'] = dt_parse('2021-04-21T11:30:00Z')
    alert_dict_2['starts_at'] = dt_parse('2021-04-21T12:30:00Z')

    assert PlannedTest(alert_dict_1) < PlannedTest(alert_dict_2)


def test_planned_test_only_has_areas():
    assert PlannedTest(
        create_planned_test_dict()
    ).areas == []

    assert PlannedTest(
        create_planned_test_dict(areas=['a', 'b'])
    ).areas == ['a', 'b']


def test_public_planned_tests_are_not_operator():
    planned_test = PlannedTest(
        create_planned_test_dict(
            channel='operator'
        ))
    assert not planned_test.is_public

    planned_test = PlannedTest(
        create_planned_test_dict(
            channel='severe'
        ))
    assert planned_test.is_public

    planned_test = PlannedTest(
        create_planned_test_dict(
            channel='government'
        ))
    assert planned_test.is_public


@freeze_time('2021-01-01T02:00:00Z')
def test_future_planned_tests_are_planned():
    planned_test = PlannedTest(
        create_planned_test_dict(
            starts_at=dt_parse('2021-01-01T01:01:01Z'),
            cancelled_at=dt_parse('2021-01-01T01:59:59Z')
        ))
    assert not planned_test.is_planned

    planned_test = PlannedTest(
        create_planned_test_dict(
            starts_at=dt_parse('2021-01-01T02:01:01Z'),
            cancelled_at=dt_parse('2021-01-01T02:59:59Z')
        ))
    assert planned_test.is_planned
