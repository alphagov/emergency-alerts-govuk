import random
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import UUID

import pytest
from dateutil.parser import parse as dt_parse

from app.models.alert import Alert
from app.models.alerts import Alerts
from app.render import (
    get_cap_xml_for_alerts,
    get_rendered_pages,
    get_url_for_alert,
)
from tests.conftest import create_alert_dict


def test_get_url_for_alert_doesnt_return_non_public_alerts():
    alerts = Alerts([
        create_alert_dict(
            channel='operator',
            starts_at=dt_parse('2021-04-21T11:30:00Z'),
        )
    ])

    with pytest.raises(ValueError):
        get_url_for_alert(alerts[0], alerts)


@pytest.mark.parametrize('index, expected_url', [
    (0, '20-apr-2021'),
    (1, '21-apr-2021'),
    (2, '21-apr-2021-2'),
    (3, '21-apr-2021-3'),
    (4, '22-apr-2021'),
])
def test_get_url_for_alert_returns_url_with_count_for_alerts_on_same_day(index, expected_url):
    the_days_alerts = [
        create_alert_dict(id=UUID(int=0), starts_at=dt_parse('2021-04-20T22:59:00Z')),
        create_alert_dict(id=UUID(int=1), starts_at=dt_parse('2021-04-20T23:00:00Z')),
        create_alert_dict(id=UUID(int=2), starts_at=dt_parse('2021-04-21T12:31:00Z')),
        create_alert_dict(id=UUID(int=3), starts_at=dt_parse('2021-04-21T12:31:00Z')),
        create_alert_dict(id=UUID(int=4), starts_at=dt_parse('2021-04-21T23:00:00Z')),
    ]

    alerts = Alerts(the_days_alerts)

    assert get_url_for_alert(Alert(the_days_alerts[index]), alerts) == expected_url


def test_get_url_for_alert_consistently_sorts_by_id():
    # all have the same start time
    the_days_alerts = [
        create_alert_dict(id=UUID(int=0)),
        create_alert_dict(id=UUID(int=1)),
        create_alert_dict(id=UUID(int=2)),
        create_alert_dict(id=UUID(int=3)),
        create_alert_dict(id=UUID(int=4)),
        create_alert_dict(id=UUID(int=5)),
        create_alert_dict(id=UUID(int=6)),
    ]

    # shuffle to make sure the order that alerts go in doesn't affect anything
    alerts = Alerts(random.sample(the_days_alerts, len(the_days_alerts)))

    assert get_url_for_alert(Alert(the_days_alerts[0]), alerts) == '21-apr-2021'
    assert get_url_for_alert(Alert(the_days_alerts[3]), alerts) == '21-apr-2021-4'
    assert get_url_for_alert(Alert(the_days_alerts[6]), alerts) == '21-apr-2021-7'


def test_get_url_for_alert_skips_non_public_alerts():
    the_days_alerts = [
        create_alert_dict(starts_at=dt_parse('2021-04-21T12:00:00Z'), channel='operator'),
        create_alert_dict(starts_at=dt_parse('2021-04-21T13:00:00Z'), channel='severe'),
    ]

    alerts = Alerts(the_days_alerts)

    # doesn't have the -2 suffix as we skip the operator alert
    assert get_url_for_alert(Alert(the_days_alerts[1]), alerts) == '21-apr-2021'


def test_get_rendered_pages_generates_atom_feed(govuk_alerts):
    the_days_alerts = [
        create_alert_dict(
            id=UUID(int=0),
            starts_at=dt_parse('2021-04-20T22:59:00Z'),
            approved_at=dt_parse('2021-04-20T23:10:00Z'),
            areas={"aggregate_names": ['England']}
        ),
        create_alert_dict(
            id=UUID(int=1),
            starts_at=dt_parse('2021-04-20T23:00:00Z'),
            approved_at=dt_parse('2021-04-20T23:11:00Z'),
            areas={"aggregate_names": ['Argyll and Bute']},
        ),
        create_alert_dict(
            id=UUID(int=2),
            starts_at=dt_parse('2021-04-21T12:31:00Z'),
            approved_at=dt_parse('2021-04-21T12:35:00Z'),
            areas={"aggregate_names": ['Scotland']},
        ),
        create_alert_dict(
            id=UUID(int=3),
            starts_at=dt_parse('2021-04-21T12:31:00Z'),
            approved_at=dt_parse('2021-04-21T12:37:00Z'),
            areas={"aggregate_names": ['Barnsley']},
        ),
        create_alert_dict(
            id=UUID(int=4),
            starts_at=dt_parse('2021-04-21T23:00:00Z'),
            approved_at=dt_parse('2021-04-21T23:09:00Z'),
            areas={"aggregate_names": ['Wales']},
        ),
    ]

    # expected feed ordered by descending date
    expected_feed_items = [
        {
            "id": "http://localhost:6017/alerts/22-apr-2021",
            "title": "Wales",
            "updated": "2021-04-21T23:09:00+00:00",
            "published": "2021-04-22T00:09:00+01:00"
        },
        {
            "id": "http://localhost:6017/alerts/21-apr-2021-3",
            "title": "Barnsley",
            "updated": "2021-04-21T12:37:00+00:00",
            "published": "2021-04-21T13:37:00+01:00"
        },
        {
            "id": "http://localhost:6017/alerts/21-apr-2021-2",
            "title": "Scotland",
            "updated": "2021-04-21T12:35:00+00:00",
            "published": "2021-04-21T13:35:00+01:00"
        },
        {
            "id": "http://localhost:6017/alerts/21-apr-2021",
            "title": "Argyll and Bute",
            "updated": "2021-04-20T23:11:00+00:00",
            "published": "2021-04-21T00:11:00+01:00"
        },
        {
            "id": "http://localhost:6017/alerts/20-apr-2021",
            "title": "England",
            "updated": "2021-04-20T23:10:00+00:00",
            "published": "2021-04-21T00:10:00+01:00"
        }
    ]

    pages = get_rendered_pages(Alerts(the_days_alerts))
    assert len(pages) > 0
    assert 'alerts/feed.atom' in pages
    assert 'alerts/feed_cy.atom' in pages

    namespace = {'atom': 'http://www.w3.org/2005/Atom'}

    feed_str = pages['alerts/feed.atom'].replace("\'", '"').replace("\n", "")
    assert '<?xml-stylesheet href="feed.xsl" type="text/xsl"?>' in feed_str
    root = ET.fromstring(feed_str)
    entries = root.findall('atom:entry', namespace)
    assert len(entries) == 5

    _verify_entries(entries, namespace, expected_feed_items)

    feed_str = pages['alerts/feed_cy.atom'].replace("\'", '"').replace("\n", "")
    assert '<?xml-stylesheet href="feed_cy.xsl" type="text/xsl"?>' in feed_str
    root = ET.fromstring(feed_str)
    entries = root.findall('atom:entry', namespace)
    assert len(entries) == 5

    _verify_entries(entries, namespace, expected_feed_items)


def _cut_off_alerts():
    # One alert last updated before the cut-off, one after.
    return [
        create_alert_dict(
            id=UUID(int=0),
            starts_at=dt_parse('2021-04-20T11:30:00Z'),
            approved_at=dt_parse('2021-04-20T11:25:00Z'),
            updated_at=dt_parse('2021-04-20T11:30:00Z'),
        ),
        create_alert_dict(
            id=UUID(int=1),
            starts_at=dt_parse('2021-04-21T11:30:00Z'),
            approved_at=dt_parse('2021-04-21T11:25:00Z'),
            updated_at=dt_parse('2021-04-22T11:30:00Z'),
        ),
    ]


def test_get_rendered_pages_without_cut_off_renders_all_alert_pages(govuk_alerts):
    pages = get_rendered_pages(Alerts(_cut_off_alerts()), cut_off=None)

    assert 'alerts/20-apr-2021' in pages
    assert 'alerts/20-apr-2021.cy' in pages
    assert 'alerts/21-apr-2021' in pages
    assert 'alerts/21-apr-2021.cy' in pages


def test_get_rendered_pages_skips_alerts_not_updated_since_cut_off(govuk_alerts):
    cut_off = dt_parse('2021-04-21T00:00:00Z')

    pages = get_rendered_pages(Alerts(_cut_off_alerts()), cut_off=cut_off)

    # Older alert (updated before cut-off) is skipped, in both languages
    assert 'alerts/20-apr-2021' not in pages
    assert 'alerts/20-apr-2021.cy' not in pages

    # Newer alert (updated after cut-off) is still rendered
    assert 'alerts/21-apr-2021' in pages
    assert 'alerts/21-apr-2021.cy' in pages

    # The atom feed remains complete regardless of the cut-off
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    feed_str = pages['alerts/feed.atom'].replace("\'", '"').replace("\n", "")
    entries = ET.fromstring(feed_str).findall('atom:entry', namespace)
    assert len(entries) == 2


def test_get_rendered_pages_skips_alerts_with_string_updated_at(govuk_alerts):
    # Alerts loaded from the API keep updated_at as an ISO string (it is not in
    # AlertsApiClient.TIMESTAMP_FIELDS), so the cut-off comparison must cope with
    # a str as well as a datetime.
    alerts = [
        create_alert_dict(
            id=UUID(int=0),
            starts_at=dt_parse('2021-04-20T11:30:00Z'),
            approved_at=dt_parse('2021-04-20T11:25:00Z'),
            updated_at='2021-04-20T11:30:00Z',
        ),
        create_alert_dict(
            id=UUID(int=1),
            starts_at=dt_parse('2021-04-21T11:30:00Z'),
            approved_at=dt_parse('2021-04-21T11:25:00Z'),
            updated_at='2021-04-22T11:30:00Z',
        ),
    ]
    cut_off = dt_parse('2021-04-21T00:00:00Z')

    pages = get_rendered_pages(Alerts(alerts), cut_off=cut_off)

    assert 'alerts/20-apr-2021' not in pages
    assert 'alerts/21-apr-2021' in pages


def _verify_entries(entries, namespace, expected):
    for i, entry in enumerate(entries):
        assert entry.find('atom:id', namespace).text == expected[i]['id']
        assert entry.find('atom:title', namespace).text == expected[i]['title']
        assert entry.find('atom:published', namespace).text == expected[i]['published']

    assert len(entries) == 5


def test_get_cap_xml_for_alerts():
    areas_dict = {
        "simple_polygons": [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]]
    }
    alerts = Alerts(
        [
            create_alert_dict(id=UUID(int=0), areas=areas_dict, cancelled_at=False),
            create_alert_dict(id=UUID(int=1), areas=areas_dict, cancelled_at=False),
            create_alert_dict(id=UUID(int=2), areas=areas_dict, cancelled_at=False),
            create_alert_dict(id=UUID(int=3), areas=areas_dict),
            create_alert_dict(id=UUID(int=4), areas=areas_dict),
            create_alert_dict(id=UUID(int=5), areas=areas_dict),
            create_alert_dict(id=UUID(int=6), areas=areas_dict),
        ]
    )
    # 7 CAP XML files for the initial alert send, 4 additional CAP XML files for the cancelled alerts
    assert len(get_cap_xml_for_alerts(alerts)) == 11

    # Generates list of filenames for all alerts
    approved_cap_xml_files = [
        f"{get_url_for_alert(alert, alerts)}-{alert.approved_at.strftime("%Y%m%d%H%M%S")}"
        for alert in alerts
    ]

    # Generates list of filenames for alerts that have been cancelled, as an extra
    # CAP XML file is created when alert is cancelled
    cancelled_cap_xml_files = [
        f"{get_url_for_alert(alert, alerts)}-{alert.cancelled_at.strftime("%Y%m%d%H%M%S")}"
        for alert in alerts
        if alert.cancelled_at
    ]
    filenames = [
        (Path(file_path).stem).split(".cap")[0]
        for file_path in get_cap_xml_for_alerts(alerts)
    ]

    expected_files = approved_cap_xml_files + cancelled_cap_xml_files

    # Asserts that the cap_xml dict keys are the filenames for all of the alerts
    assert filenames.sort() == expected_files.sort()


def test_get_cap_xml_for_alerts_skips_non_public_alerts():
    # Asserts that CAP XML only created for public alerts, not Operator alerts
    alerts = Alerts(
        [
            create_alert_dict(id=UUID(int=0), channel="operator"),
            create_alert_dict(id=UUID(int=1), channel="operator"),
            create_alert_dict(id=UUID(int=2), channel="operator"),
            create_alert_dict(id=UUID(int=3), channel="operator"),
        ]
    )
    assert get_cap_xml_for_alerts(alerts) == {}
