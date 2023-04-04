import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.planned_test import PlannedTest
from tests import normalize_spaces


@pytest.mark.parametrize('data_from_yaml, expected_h2s, expected_h3s, expected_paragraphs', (
    (
        [PlannedTest({
            'id': '1513b353-685e-488e-9547-4e1ce7359051',
            'channel': 'severe',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-02-03T20:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-02-03T22:00:00Z'),
            'content': 'This is a mobile network operator test of the Emergency Alerts '
                       'service. You do not need to take any action. To find out more, '
                       'search for gov.uk/alerts',
            'areas': {'names': ['Ibiza']}
        })],
        ['Wednesday 3 February 2021 at 8pm', 'Ibiza'],
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
            'channel': 'severe',
            'approved_at': dt_parse('2021-02-01T23:00:00Z'),
            'starts_at': dt_parse('2021-02-03T20:00:00Z'),
            'cancelled_at': None,
            'finishes_at': dt_parse('2021-02-03T22:00:00Z'),
            'content': 'Paragraph 1\n\nParagraph 2',
            'areas': {'names': ['Ibiza', 'The Norfolk Broads']}
        })],
        ['Wednesday 3 February 2021 at 8pm', 'Ibiza and The Norfolk Broads'],
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
            'Wednesday 3 February 2021 at 8pm', '', ''
        ],
        [],
        [
            'There will be a service test of the UK Emergency Alerts system today.',
            'Most mobile phones and tablets will not get a test alert.',
            'Find out more about testing the Emergency Alerts service.',
            'The alert will say:',
            'Paragraph 1',
            'Paragraph 2',
            'There will be a service test of the UK Emergency Alerts system today.',
            'Most mobile phones and tablets will not get a test alert.',
            'Find out more about testing the Emergency Alerts service.',
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
    html = client_get("alerts/announcements")
    assert [
        normalize_spaces(h2.text) for h2 in html.select('main .govuk-grid-column-two-thirds h2')
    ] == expected_h2s
    assert [
        normalize_spaces(h3.text) for h3 in html.select('main .govuk-grid-column-two-thirds h3')
    ] == expected_h3s
    assert [
        normalize_spaces(p.text) for p in html.select('main .govuk-grid-column-two-thirds p')
    ] == expected_paragraphs
