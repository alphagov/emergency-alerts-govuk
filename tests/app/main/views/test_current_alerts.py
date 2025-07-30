from app.models.alerts import Alerts
from tests import normalize_spaces
from tests.conftest import create_alert_dict


def test_current_alerts_page(client_get):
    html = client_get("alerts/current-alerts")
    assert html.select_one("h1").text.strip() == "Current alerts"


def test_current_alerts_page_shows_single_alert(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch("app.models.alert.Alert.display_areas", ["foo"])
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    body = html.select("p.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to Foo"
    assert body[0].text.strip() == "Something"
    assert body[1].text.strip() == (
        'Sent by the UK government at 12:30pm on Wednesday 21 April 2021'
    )
    assert body[2].text.strip() == (
        'This alert was sent to foo.'
    )


def test_current_alerts_page_shows_multiple_alerts(
    alert_dict,
    client_get,
    mocker,
    sample_content
):
    mocker.patch("app.models.alert.Alert.display_areas", ["foo"])
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([create_alert_dict(content=sample_content),
                                                                       alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    truncated_content = html.select('p.truncated-text')
    links = html.select('a.govuk-body')

    assert len(titles) == 2
    assert titles[0].text.strip() == titles[1].text.strip() == "Emergency alert sent to Foo"
    assert truncated_content[0].text.strip() == sample_content
    assert truncated_content[1].text.strip() == "Something"
    assert len(links) == 2


def test_current_alerts_page_shows_postcode_area_alerts(
    alert_dict,
    client_get,
    mocker,
    sample_content
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "4km around the postcode BD1 1EE, in Bradford",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([create_alert_dict(content=sample_content)]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    body = html.select("p.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to An area in Bradford"
    assert ' '.join(
        [normalize_spaces(p.text) for p in body]
    ) == normalize_spaces(
        f"""{sample_content} Sent by the UK government at 12:30pm on Wednesday 21 April 2021
            This alert was sent to an area in Bradford.
            Surrounding areas might also have received the alert."""
    )


def test_current_alerts_page_shows_decimal_coordinate_area_alerts(
    alert_dict,
    client_get,
    mocker,
    sample_content
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "5km around 54.0 latitude, -2.0 longitude, in Craven",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([create_alert_dict(content=sample_content)]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    body = html.select("p.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to An area in Craven"
    assert ' '.join(
        [normalize_spaces(p.text) for p in body]
    ) == normalize_spaces(
        f"""{sample_content} Sent by the UK government at 12:30pm on Wednesday 21 April 2021
            This alert was sent to an area in Craven.
            Surrounding areas might also have received the alert."""
    )


def test_current_alerts_page_shows_cartesian_coordinate_area_alerts(
    alert_dict,
    client_get,
    mocker,
    sample_content
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "10km around the easting of 530111.0 and the northing of 170000.0 in Lambeth",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([create_alert_dict(content=sample_content)]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    body = html.select("p.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to An area in Lambeth"
    assert ' '.join(
        [normalize_spaces(p.text) for p in body]
    ) == normalize_spaces(
        f"""{sample_content} Sent by the UK government at 12:30pm on Wednesday 21 April 2021
            This alert was sent to an area in Lambeth.
            Surrounding areas might also have received the alert."""
    )


def test_current_alerts_page_shows_cartesian_coordinate_area_alerts_without_local_authority(
    alert_dict,
    client_get,
    mocker,
    sample_content
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "10km around the easting of 530111.0 and the northing of 170000.0",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([create_alert_dict(content=sample_content)]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    body = html.select("p.govuk-body")

    assert len(titles) == 1
    assert (
        titles[0].text.strip()
        == "Emergency alert sent to 10km around the easting of 530111.0 and the northing of 170000.0"
    )
    assert ' '.join(
        [normalize_spaces(p.text) for p in body]
    ) == normalize_spaces(
        f"""{sample_content} Sent by the UK government at 12:30pm on Wednesday 21 April 2021
            This alert was sent to 10km around the easting of 530111.0 and the northing of 170000.0.
            Surrounding areas might also have received the alert."""
    )
