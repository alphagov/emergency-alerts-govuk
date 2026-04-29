import builtins
from unittest.mock import mock_open, patch

import boto3
import pytest
from flask import current_app
from moto import mock_aws

from app.tasks.tasks import (
    publish_govuk_alerts,
    trigger_govuk_alerts_healthcheck,
)


@patch("app.models.publish_task_progress.PublishTaskProgress.create")
@patch("app.notify_client.alerts_api_client.publish_api_client.create_publish_task")
@patch("app.tasks.tasks.PublishTaskProgress.update_progress")
@patch("app.notify_client.alerts_api_client.publish_api_client.update_publish_task")
@patch("app.tasks.tasks.Alerts.load")
@patch("app.tasks.tasks.get_rendered_pages")
@patch("app.tasks.tasks.upload_html_to_s3")
@patch("app.tasks.tasks.purge_fastly_cache")
@patch("app.tasks.tasks.alerts_api_client.send_publish_acknowledgement")
@patch("app.notify_client.alerts_api_client.publish_api_client.mark_publish_as_finished")
def test_publish_govuk_alerts(
    mock_mark_publish_as_finished,
    mock_send_publish_acknowledgement,
    mock_purge_fastly_cache,
    mock_upload_to_s3,
    mock_get_rendered_pages,
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
    mock_Alerts_load.assert_called_once_with(mock_create_progress.return_value)
    mock_get_rendered_pages.assert_called_once_with(
        mock_Alerts_load.return_value,
        mock_create_progress.return_value,
    )
    mock_upload_to_s3.assert_called_once_with(
        mock_get_rendered_pages.return_value,
        mock_create_progress.return_value
    )
    mock_purge_fastly_cache.assert_called_once()
    mock_send_publish_acknowledgement.assert_called_once()
    mock_publish_task.set_to_finished.assert_called_once_with()


class BubbledException(Exception):
    pass


@patch("app.models.publish_task_progress.PublishTaskProgress.create")
@patch("app.tasks.tasks.Alerts.load")
@patch("app.tasks.tasks.get_rendered_pages")
@patch("app.tasks.tasks.upload_html_to_s3")
@pytest.mark.xfail(raises=BubbledException)
def test_publish_govuk_alerts_bubbles_for_retry(
    mock_upload_to_s3,
    mock_get_rendered_pages,
    mock_Alerts_load,
    mock_create_progress,
    govuk_alerts,
):
    # The retry logic here is based around the idea we should bubble exceptions, and
    # that the actor is registered for retry
    assert publish_govuk_alerts.kw.get("allow_retry")
    mock_upload_to_s3.side_effect = BubbledException("Error for retry")
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
