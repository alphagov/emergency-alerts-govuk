import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alert import PlannedTest
from app.models.alerts import Alerts
from tests import normalize_spaces
from tests.conftest import create_alert_dict


def test_planned_tests_page(mocker, client_get):
    mocker.patch('app.models.alerts.PlannedTests.from_yaml', return_value=[])
    html = client_get("alerts/planned-tests")
    assert html.select_one('h1').text.strip() == "Planned tests"
    assert [
        normalize_spaces(p.text) for p in html.select('main p')
    ] == [
        'There are currently no planned tests of emergency alerts.',
        'You can see previous tests on the past alerts page.',
    ]
    assert html.select_one('main p a').text == 'past alerts page'
    assert html.select_one('main p a')['href'] == '/alerts/past-alerts'


@pytest.mark.parametrize('data_from_yaml, expected_h2s, expected_h3s, expected_paragraphs', (
    (
        [PlannedTest({
            'starts_at': '2021-02-03T00:00:00Z',
            'content': None,
            'display_areas': [],
        })],
        ['Wednesday 3 February 2021'],
        [],
        [
            'Some mobile phone networks in the UK will test emergency alerts.',
            'Most phones and tablets will not get a test alert.',
            'Find out more about mobile network operator tests.',
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
            'starts_at': '2021-02-03T23:00:00Z',
            'content': 'Paragraph 1\n\nParagraph 2',
            'display_areas': ['Ibiza', 'The Norfolk Broads'],
        })],
        ['Wednesday 3 February 2021'],
        ['Planned test will be sent to Ibiza and The Norfolk Broads'],
        [
            'Paragraph 1',
            'Paragraph 2',
        ]
    ),
    (
        [
            PlannedTest({
                'starts_at': '2021-02-03T00:00:00Z',
                'content': 'Paragraph 1\n\nParagraph 2',
                'display_areas': ['Ibiza'],
            }),
            PlannedTest({
                'starts_at': '2021-02-03T01:00:00Z',
                'content': 'Paragraph 3\n\nParagraph 4',
                'display_areas': ['The Norfolk Broads'],
            }),
        ],
        [
            # Not aggregated because it’s unlikely we’ll plan two
            # different tests on the same day
            'Wednesday 3 February 2021', 'Wednesday 3 February 2021'
        ],
        [
            'Planned test will be sent to Ibiza',
            'Planned test will be sent to The Norfolk Broads'],
        [
            'Paragraph 1',
            'Paragraph 2',
            'Paragraph 3',
            'Paragraph 4',
        ]
    ),
))
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
        normalize_spaces(h2.text) for h2 in html.select('main h2')
    ] == expected_h2s
    assert [
        normalize_spaces(h3.text) for h3 in html.select('main h3')
    ] == expected_h3s
    assert [
        normalize_spaces(p.text) for p in html.select('main p')
    ] == expected_paragraphs


@pytest.mark.parametrize('extra_json_fields', (
    # Doesn’t matter if the alert is still active…
    {},
    # Or if it’s cancelled before now
    {'cancelled_at': dt_parse('2021-04-21T10:00:00Z')},
    # Or if it’s finished already
    {'finishes_at': dt_parse('2021-04-21T10:00:00Z')},
))
@freeze_time('2021-04-21T11:00:00Z')
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
            **extra_json_fields
        )
    ]))
    html = client_get("alerts/planned-tests")
    assert [
        normalize_spaces(h2.text) for h2 in html.select('main h2')
    ] == [
        'Wednesday 21 April 2021'
    ]
    assert not html.select('main h3')
    assert [
        normalize_spaces(p.text) for p in html.select('main p')
    ] == [
        'Something'
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
        )
    ]))
    html = client_get("alerts/planned-tests")
    assert normalize_spaces(html.select_one('main p').text) == (
        'There are currently no planned tests of emergency alerts.'
    )
