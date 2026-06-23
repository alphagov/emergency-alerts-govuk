import builtins
from datetime import datetime, timezone
from unittest.mock import mock_open, patch

import boto3
import pytest
from flask import current_app
from moto import mock_aws

from app.tasks.tasks import (
    publish_govuk_alerts,
    publish_govuk_alerts_full,
    trigger_govuk_alerts_healthcheck,
)


@patch("app.models.publish_task_progress.PublishTaskProgress.create")
@patch("app.notify_client.alerts_api_client.publish_api_client.create_publish_task")
@patch("app.tasks.tasks.PublishTaskProgress.update_progress")
@patch("app.notify_client.alerts_api_client.publish_api_client.update_publish_task")
@patch("app.tasks.tasks.Alerts.load")
@patch("app.tasks.tasks.get_publish_destination")
@patch("app.tasks.tasks.get_rendered_pages")
@patch("app.tasks.tasks.get_cap_xml_for_alerts")
@patch("app.tasks.tasks.prepare_destination")
@patch("app.tasks.tasks.restore_latest_archive")
@patch("app.tasks.tasks.upload_html_to_s3")
@patch("app.tasks.tasks.upload_cap_xml_to_s3")
@patch("app.tasks.tasks.purge_fastly_cache")
@patch("app.tasks.tasks.alerts_api_client.send_publish_acknowledgement")
@patch("app.notify_client.alerts_api_client.publish_api_client.mark_publish_as_finished")
@patch("app.tasks.tasks.archive_website")
@patch("app.tasks.tasks._get_govuk_archive_timestamp")
def test_publish_govuk_alerts(
    mock_get_archive_timestamp,
    mock_archive_website,
    mock_mark_publish_as_finished,
    mock_send_publish_acknowledgement,
    mock_purge_fastly_cache,
    mock_upload_cap_xml_to_s3,
    mock_upload_to_s3,
    mock_restore_latest_archive,
    mock_prepare_destination,
    mock_get_cap_xml,
    mock_get_rendered_pages,
    mock_get_publish_destination,
    mock_Alerts_load,
    mock_update_publish_task,
    mock_update_progress,
    mock_create_publish_task,
    mock_create_progress,
    govuk_alerts,
):
    publish_govuk_alerts()
    mock_create_progress.assert_called_once_with(
        publish_type="publish-dynamic", publish_origin="dramatiq"
    )
    mock_publish_task = mock_create_progress.return_value
    mock_get_publish_destination.assert_called_once()
    mock_prepare_destination.assert_called_once_with(mock_get_publish_destination.return_value)
    mock_restore_latest_archive.assert_called_once_with(mock_get_publish_destination.return_value)
    mock_Alerts_load.assert_called_once_with(mock_create_progress.return_value)
    mock_get_rendered_pages.assert_called_once_with(
        mock_Alerts_load.return_value,
        cut_off=mock_get_archive_timestamp.return_value,
        publish_task_progress=mock_create_progress.return_value,
    )
    mock_get_cap_xml.assert_called_once_with(
        mock_Alerts_load.return_value,
        cut_off=mock_get_archive_timestamp.return_value,
        publish_task_progress=mock_create_progress.return_value,
    )
    mock_upload_to_s3.assert_called_once_with(
        mock_get_rendered_pages.return_value,
        mock_get_publish_destination.return_value,
        mock_create_progress.return_value
    )
    mock_upload_cap_xml_to_s3.assert_called_once_with(
        mock_get_cap_xml.return_value,
        mock_get_publish_destination.return_value,
        mock_create_progress.return_value,
    )
    mock_purge_fastly_cache.assert_called_once()
    mock_send_publish_acknowledgement.assert_called_once()
    mock_publish_task.set_to_finished.assert_called_once_with()
    mock_archive_website.assert_called_once()


@patch("app.models.publish_task_progress.PublishTaskProgress.create")
@patch("app.notify_client.alerts_api_client.publish_api_client.create_publish_task")
@patch("app.tasks.tasks.PublishTaskProgress.update_progress")
@patch("app.notify_client.alerts_api_client.publish_api_client.update_publish_task")
@patch("app.tasks.tasks.Alerts.load")
@patch("app.tasks.tasks.get_publish_destination")
@patch("app.tasks.tasks.get_rendered_pages")
@patch("app.tasks.tasks.get_cap_xml_for_alerts")
@patch("app.tasks.tasks.prepare_destination")
@patch("app.tasks.tasks.upload_assets_to_s3")
@patch("app.tasks.tasks.upload_html_to_s3")
@patch("app.tasks.tasks.upload_cap_xml_to_s3")
@patch("app.tasks.tasks.purge_fastly_cache")
@patch("app.tasks.tasks.alerts_api_client.send_publish_acknowledgement")
@patch("app.notify_client.alerts_api_client.publish_api_client.mark_publish_as_finished")
@patch("app.tasks.tasks.archive_website")
@patch("app.tasks.tasks._get_govuk_archive_timestamp")
def test_publish_govuk_alerts_full(
    mock_get_archive_timestamp,
    mock_archive_website,
    mock_mark_publish_as_finished,
    mock_send_publish_acknowledgement,
    mock_purge_fastly_cache,
    mock_upload_cap_xml_to_s3,
    mock_upload_to_s3,
    mock_upload_assets_to_s3,
    mock_prepare_destination,
    mock_get_cap_xml,
    mock_get_rendered_pages,
    mock_get_publish_destination,
    mock_Alerts_load,
    mock_update_publish_task,
    mock_update_progress,
    mock_create_publish_task,
    mock_create_progress,
    govuk_alerts,
):
    publish_govuk_alerts_full()
    mock_create_progress.assert_called_once_with(
        publish_type="publish-dynamic", publish_origin="dramatiq"
    )
    mock_publish_task = mock_create_progress.return_value
    mock_get_publish_destination.assert_called_once()
    mock_prepare_destination.assert_called_once_with(mock_get_publish_destination.return_value)
    mock_upload_assets_to_s3.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value,
    )
    mock_Alerts_load.assert_called_once_with(mock_create_progress.return_value)
    mock_get_rendered_pages.assert_called_once_with(
        mock_Alerts_load.return_value,
        cut_off=datetime(1970, 1, 1, tzinfo=timezone.utc),
        publish_task_progress=mock_create_progress.return_value,
    )
    mock_get_cap_xml.assert_called_once_with(
        mock_Alerts_load.return_value,
        cut_off=datetime(1970, 1, 1, tzinfo=timezone.utc),
        publish_task_progress=mock_create_progress.return_value,
    )
    mock_upload_to_s3.assert_called_once_with(
        mock_get_rendered_pages.return_value,
        mock_get_publish_destination.return_value,
        mock_create_progress.return_value
    )
    mock_upload_cap_xml_to_s3.assert_called_once_with(
        mock_get_cap_xml.return_value,
        mock_get_publish_destination.return_value,
        mock_create_progress.return_value,
    )
    mock_purge_fastly_cache.assert_called_once()
    mock_send_publish_acknowledgement.assert_called_once()
    mock_publish_task.set_to_finished.assert_called_once_with()
    mock_archive_website.assert_called_once()


class BubbledException(Exception):
    pass


@patch("app.models.publish_task_progress.PublishTaskProgress.create")
@patch("app.tasks.tasks.Alerts.load")
@patch("app.tasks.tasks.get_publish_destination")
@patch("app.tasks.tasks.get_rendered_pages")
@patch("app.tasks.tasks.upload_html_to_s3")
@pytest.mark.xfail(raises=BubbledException)
def test_publish_govuk_alerts_bubbles_for_retry(
    mock_upload_to_s3,
    mock_get_rendered_pages,
    mock_get_publish_destination,
    mock_Alerts_load,
    mock_create_progress,
    govuk_alerts,
):
    # The retry logic here is based around the idea we should bubble exceptions, and
    # that the actor is registered for retry
    assert publish_govuk_alerts.kw.get("allow_retry")
    mock_get_publish_destination.side_effect = BubbledException("Error for retry")
    publish_govuk_alerts()


# Mock only open() for the healthcheck path, but allow others (botocore) to read
# normally for its internal init logic
def open_for_healthcheck(original_open):
    def side_effect(*args, **kwargs):
        if args[0] == "/eas/emergency-alerts-govuk/celery-beat-healthcheck":
            return mock_open()()
        return original_open(*args, **kwargs)

    return side_effect


@mock_aws
def test_govuk_alerts_healthcheck_posts_to_cloudwatch(mocker, govuk_alerts):
    with patch.object(builtins, "open", side_effect=open_for_healthcheck(open)):
        trigger_govuk_alerts_healthcheck()

    cloudwatch = boto3.client(
        "cloudwatch", region_name=current_app.config["AWS_REGION"]
    )
    metric = cloudwatch.list_metrics()["Metrics"][0]
    assert metric["MetricName"] == "AppVersion"
    assert metric["Namespace"] == "Emergency Alerts"
    assert {"Name": "Application", "Value": "govuk"} in metric["Dimensions"]
