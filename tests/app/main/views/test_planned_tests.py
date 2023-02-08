import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alerts import Alerts
from app.models.planned_test import PlannedTest
from tests import normalize_spaces
from tests.conftest import create_alert_dict


def test_planned_tests_page(mocker, client_get):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    html = client_get("alerts/planned-tests")
    assert html.select_one('h1').text.strip() == "Planned tests"
    assert [
        normalize_spaces(p.text) for p in html.select('main p')
    ] == [
        'There are currently no planned tests.'
    ]


@pytest.mark.parametrize('data_from_yaml, expected_h2s, expected_h3s, expected_paragraphs', (
    (
        [PlannedTest({
            'id': '1513b353-685e-488e-9547-4e1ce7359051',
            'channel': 'operator',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-02-03T20:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-02-03T22:00:00Z'),
            'content': 'This is a mobile network operator test of the Emergency Alerts '
                       'service. You do not need to take any action. To find out more, '
                       'search for gov.uk/alerts',
            'areas': {'names': ['Ibiza']}
        })],
        ['Wednesday 3 February 2021', 'Ibiza'],
        [],
        [
            'The alert will say:',
            (
                'This is a mobile network operator test of the Emergency Alerts '
                'service. You do not need to take any action. To find out more, '
                'search for gov.uk/alerts'
            ),
        ]
    ),
    (
        [PlannedTest({
            'id': '4775b57c-3ad0-4270-a9e0-9ece3171aa9b',
            'channel': 'operator',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-02-03T20:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-02-03T22:00:00Z'),
            'content': 'Paragraph 1\n\nParagraph 2',
            'areas': {'names': ['Ibiza', 'The Norfolk Broads']}
        })],
        ['Wednesday 3 February 2021', 'Ibiza and The Norfolk Broads'],
        [],
        [
            'The alert will say:',
            'Paragraph 1',
            'Paragraph 2',
        ]
    ),
    (
        [
            PlannedTest({
                'id': 'eda516fc-47bd-445e-b49b-6fd4eeaff7d5',
                'channel': 'operator',
                'approved_at': dt_parse('2021-02-01T23:00:00Z'),
                'starts_at': dt_parse('2021-02-03T20:00:00Z'),
                'cancelled_at': None,
                'finishes_at': dt_parse('2021-02-03T22:00:00Z'),
                'content': 'Paragraph 1\n\nParagraph 2',
                'areas': {'names': ['Ibiza']}
            }),
            PlannedTest({
                'id': '5838d0d7-37eb-4ec9-87a7-5d9dc5b650c3',
                'channel': 'operator',
                'approved_at': dt_parse('2021-02-01T23:00:00Z'),
                'starts_at': dt_parse('2021-02-03T20:00:00Z'),
                'cancelled_at': None,
                'finishes_at': dt_parse('2021-02-03T22:00:00Z'),
                'content': 'Paragraph 3\n\nParagraph 4',
                'areas': {'names': ['The Norfolk Broads']}
            }),
        ],
        [
            'Wednesday 3 February 2021', 'Ibiza', 'The Norfolk Broads'
        ],
        [],
        [
            'The alert will say:',
            'Paragraph 1',
            'Paragraph 2',
            "The alert will say:",
            'Paragraph 3',
            'Paragraph 4',
        ]
    ),
))
@freeze_time('2021-01-01T11:00:00Z')
def test_planned_tests_page_with_upcoming_test(
    mocker,
    client_get,
    data_from_yaml,
    expected_h2s,
    expected_h3s,
    expected_paragraphs,
):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=data_from_yaml)
    html = client_get("alerts/planned-tests")
    assert [
        normalize_spaces(h2.text) for h2 in html.select('main .govuk-grid-column-two-thirds h2')
    ] == expected_h2s
    assert [
        normalize_spaces(h3.text) for h3 in html.select('main .govuk-grid-column-two-thirds h3')
    ] == expected_h3s
    assert [
        normalize_spaces(p.text) for p in html.select('main .govuk-grid-column-two-thirds p')
    ] == expected_paragraphs


@pytest.mark.parametrize('extra_json_fields', (
    # Doesn’t matter if the alert is still active…
    {},
    # Or if it’s cancelled before now
    {'cancelled_at': dt_parse('2021-04-21T11:00:00Z')},
    # Or if it’s finished already
    {'finishes_at': dt_parse('2021-04-21T11:00:00Z')},
))
@freeze_time('2021-04-21T10:00:00Z')
def test_planned_tests_page_with_current_operator_test(
    mocker,
    client_get,
    extra_json_fields,
):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            channel='operator',
            starts_at=dt_parse('2021-04-21T09:00:00Z'),
            content='This is a mobile network operator test of the Emergency Alerts '
                    'service. You do not need to take any action. To find out more, '
                    'search for gov.uk/alerts',
            **extra_json_fields
        )
    ]))
    html = client_get("alerts/planned-tests")
    assert [
        normalize_spaces(h2.text) for h2 in html.select('.govuk-grid-column-two-thirds h2')
    ] == [
        'Wednesday 21 April 2021', "None"
    ]
    assert not html.select('main h3')
    assert [
        normalize_spaces(p.text) for p in html.select('.govuk-grid-column-two-thirds p')
    ] == [
        'The alert will say:',
        (
            'This is a mobile network operator test of the Emergency Alerts '
            'service. You do not need to take any action. To find out more, '
            'search for gov.uk/alerts'
        ),
    ]


@freeze_time('2021-04-21T11:00:00Z')
def test_planned_tests_page_with_previous_days_operator_test(
    mocker,
    client_get,
):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            channel='operator',
            starts_at=dt_parse('2021-04-20T09:00:00Z'),
            finishes_at=dt_parse('2021-04-20T10:00:00Z'),
            cancelled_at=None,
        )
    ]))
    html = client_get("alerts/planned-tests")
    assert normalize_spaces(html.select_one('main p').text) == (
        'There are currently no planned tests.'
    )
