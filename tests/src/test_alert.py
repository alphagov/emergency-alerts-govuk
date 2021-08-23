import pytest

from app.models.alert import Alert


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
    mocker.patch('app.models.alerts.Alerts.public', [Alert(alert_dict)])
    mocker.patch(__name__ + '.Alert.is_expired', is_expired)

    html = client_get('alerts/1234')
    assert html.select('.govuk-breadcrumbs__link')[2].text == breadcrumb
