from datetime import datetime
from uuid import uuid4

import pytest
from freezegun import freeze_time

from app.models.alerts import Alerts
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
        create_alert_dict(id=uuid4(), content='test 1', starts_at=datetime(2021, 4, 21, 11, 0)),
        create_alert_dict(id=uuid4(), content='test 2', starts_at=datetime(2021, 4, 21, 12, 0))
    ]))

    html = client_get('alerts/21-apr-2021-2')
    assert html.select_one('.share-url p').text.strip() == 'https://www.gov.uk/alerts/21-apr-2021-2'
    assert html.select('p.govuk-body-l')[0].text == 'test 2'
    assert html.select('p.govuk-body')[0].text.strip() == (
        'Sent by the UK government at 1:00pm on Wednesday 21 April 2021'
    )


@freeze_time('2021-04-21T17:00:00')
def test_alert_says_expired_alert_stopped(client_get, mocker):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            id=uuid4(),
            content='test 1',
            starts_at=datetime(2021, 4, 21, 11, 0),
            cancelled_at=None,
            finishes_at=datetime(2021, 4, 21, 15, 0),
        )
    ]))

    html = client_get('alerts/21-apr-2021')
    assert html.select_one('main h2').text.strip() == 'Stopped sending at 4:00pm on Wednesday 21 April 2021'


@freeze_time('2021-04-21T14:00:00')
def test_alert_says_active_alert_is_active(client_get, mocker):
    mocker.patch('app.models.alerts.Alerts.load', return_value=Alerts([
        create_alert_dict(
            id=uuid4(),
            content='test 1',
            starts_at=datetime(2021, 4, 21, 11, 0),
            cancelled_at=None,
            finishes_at=datetime(2021, 4, 21, 15, 0),
        )
    ]))

    html = client_get('alerts/21-apr-2021')
    # no "Stopped sending at ..." h2
    assert html.find('main h2') is None
