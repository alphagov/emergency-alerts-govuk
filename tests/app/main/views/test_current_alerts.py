from app.models.alerts import Alerts


def test_current_alerts_page(client_get):
    html = client_get("alerts/current-alerts")
    assert html.select_one("h1").text.strip() == "Current alerts"


def test_current_alerts_page_shows_alerts(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch("app.models.alert.Alert.display_areas", ["foo"])
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    link = html.select_one("a.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to Foo"
    assert "More information about this alert" in link.text


def test_current_alerts_page_shows_postcode_area_alerts(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "4km around the postcode BD1 1EE, in Bradford",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    link = html.select_one("a.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to An area in Bradford"
    assert "More information about this alert" in link.text


def test_current_alerts_page_shows_decimal_coordinate_area_alerts(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "5km around 54.0 latitude, -2.0 longitude, in Craven",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    link = html.select_one("a.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to An area in Craven"
    assert "More information about this alert" in link.text


def test_current_alerts_page_shows_cartesian_coordinate_area_alerts(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "10km around the easting of 530111.0 and the northing of 170000.0 in Lambeth",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    link = html.select_one("a.govuk-body")

    assert len(titles) == 1
    assert titles[0].text.strip() == "Emergency alert sent to An area in Lambeth"
    assert "More information about this alert" in link.text


def test_current_alerts_page_shows_cartesian_coordinate_area_alerts_without_local_authority(
    alert_dict,
    client_get,
    mocker,
):
    mocker.patch(
        "app.models.alert.Alert.display_areas",
        [
            "10km around the easting of 530111.0 and the northing of 170000.0",
        ],
    )
    mocker.patch("app.models.alert.Alert.is_current_and_public", return_value=True)
    mocker.patch("app.models.alerts.Alerts.load", return_value=Alerts([alert_dict]))

    html = client_get("alerts/current-alerts")
    titles = html.select("h2.alerts-alert__title")
    link = html.select_one("a.govuk-body")

    assert len(titles) == 1
    assert (
        titles[0].text.strip()
        == "Emergency alert sent to 10km around the easting of 530111.0 and the northing of 170000.0"
    )
    assert "More information about this alert" in link.text
