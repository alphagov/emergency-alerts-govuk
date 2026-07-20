from uuid import uuid4

import pytest
from dateutil.parser import parse as dt_parse
from freezegun import freeze_time

from app.models.alerts import Alerts
from tests import normalize_spaces
from tests.conftest import create_alert_dict


@pytest.mark.parametrize('is_expired,breadcrumb', [
    [True, 'Past alerts'],
    [False, 'Current alerts']
])
def test_alert_breadcrumbs(
    is_expired,
    breadcrumb,
    client_get,
    alert_dict,
    mocker,
):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([alert_dict]))
    mocker.patch('app.models.alert.Alert.is_expired', is_expired)

    html = client_get('alerts/21-apr-2021')
    assert html.select('.govuk-breadcrumbs__link')[2].text == breadcrumb


@pytest.mark.parametrize('is_expired', [True, False])
def test_alert_links_to_correct_page_based_on_url_slug(is_expired, client_get, mocker):
    mocker.patch('app.models.alert.Alert.is_expired', is_expired)
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(id=uuid4(), content='test 1', starts_at=dt_parse('2021-04-21T11:00:00Z')),
        create_alert_dict(id=uuid4(), content='test 2', starts_at=dt_parse('2021-04-21T12:00:00Z')),
    ]))

    html = client_get('alerts/21-apr-2021-2')
    assert html.select('p.govuk-body')[0].text == 'test 2'
    assert html.select('p.govuk-body')[1].text.strip() == (
        'Sent by the UK government at 1:00pm on Wednesday 21 April 2021'
    )


@freeze_time('2021-04-21T17:00:00')
def test_alert_says_expired_alert_stopped(client_get, mocker):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            id=uuid4(),
            content='test 1',
            starts_at=dt_parse('2021-04-21T11:00:00Z'),
            cancelled_at=None,
            finishes_at=dt_parse('2021-04-21T15:00:00Z'),
            extra_content="Test Extra Content"
        )
    ]))

    html = client_get('alerts/21-apr-2021')
    assert html.select_one('main h2').text.strip() == 'Stopped sending at 4:00pm on Wednesday 21 April 2021'
    assert html.select_one('p.govuk-body').text.strip() == "test 1"
    assert ' '.join([
        normalize_spaces(p.text) for p in html.select('#extra-content p')
    ]) == "Additional Information Test Extra Content"


@freeze_time('2021-04-21T14:00:00Z')
def test_alert_says_active_alert_is_active(client_get, mocker):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            id=uuid4(),
            content='test 1',
            starts_at=dt_parse('2021-04-21T11:00:00Z'),
            cancelled_at=None,
            finishes_at=dt_parse('2021-04-21T15:00:00Z'),
        )
    ]))

    html = client_get('alerts/21-apr-2021')
    # no "Stopped sending at ..." h2
    assert html.find('main h2') is None


@pytest.mark.parametrize('url, expected_href_attribute', (
    (
        'gov.uk/alerts',
        'http://gov.uk/alerts',
    ),
    (
        'https://example.com/?a=foo&b=%22bar%22#baz',
        'https://example.com/?a=foo&b=%22bar%22#baz',
    ),
))
def test_urls_in_alerts_are_clickable(client_get, mocker, url, expected_href_attribute):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            id=uuid4(),
            content=f'go to {url}',
            starts_at=dt_parse('2021-04-21T11:00:00Z'),
        ),
    ]))

    html = client_get('alerts/21-apr-2021')
    link = html.select_one('p.govuk-body a.govuk-link')
    assert link['href'] == expected_href_attribute
    assert link.text == url


@pytest.mark.parametrize('extra_content', (('TEST 1', 'Test 2')))
def test_alert_displays_extra_content_if_exists(client_get, mocker, extra_content):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(id=uuid4(), content='test 1', starts_at=dt_parse('2021-04-21T11:00:00Z'),
                          extra_content=extra_content)]))

    html = client_get('alerts/21-apr-2021')

    assert ' '.join([
        normalize_spaces(p.text) for p in html.select('#extra-content p')
    ]) == f"Additional Information {extra_content}"


def test_alert_no_extra_content(client_get, mocker):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(id=uuid4(), content='test 1', starts_at=dt_parse('2021-04-21T11:00:00Z'))]))

    html = client_get('alerts/21-apr-2021')
    assert not html.select_one('#extra-content')
