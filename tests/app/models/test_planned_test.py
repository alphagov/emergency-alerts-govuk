from dateutil.parser import parse as dt_parse

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
