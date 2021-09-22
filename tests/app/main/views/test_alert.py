import pytest

from app.models.alerts import Alerts


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
