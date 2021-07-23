import pytest

from lib.alert import Alert
from tests.conftest import render_template


@pytest.mark.parametrize('is_expired_or_test,breadcrumb', [
    [True, 'Past alerts'],
    [False, 'Current alerts']
])
def test_alert_breadcrumbs(
    is_expired_or_test,
    breadcrumb,
    env,
    alert_dict,
    mocker,
):
    mocker.patch(__name__ + '.Alert.is_expired_or_test', is_expired_or_test)
    html = render_template(env, 'src/alert.html', {'alert_data': Alert(alert_dict)})
    assert html.select('.govuk-breadcrumbs__link')[2].text == breadcrumb
