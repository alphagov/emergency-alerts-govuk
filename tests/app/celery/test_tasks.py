import builtins
from unittest.mock import mock_open, patch

import boto3
import pytest
from celery.exceptions import Retry
from flask import current_app
from moto import mock_aws

from app.celery.tasks import (
    publish_govuk_alerts,
    trigger_govuk_alerts_healthcheck,
)


@patch("app.celery.tasks.Alerts.load")
@patch("app.celery.tasks.get_rendered_pages")
@patch("app.celery.tasks.upload_html_to_s3")
@patch("app.celery.tasks.purge_fastly_cache")
@patch("app.celery.tasks.alerts_api_client.send_publish_acknowledgement")
def test_publish_govuk_alerts(
    mock_send_publish_acknowledgement,
    mock_purge_fastly_cache,
    mock_upload_to_s3,
    mock_get_rendered_pages,
    mock_Alerts_load,
    govuk_alerts,
):
    publish_govuk_alerts()
    mock_Alerts_load.assert_called_once()
    mock_get_rendered_pages.assert_called_once_with(mock_Alerts_load.return_value)
    mock_upload_to_s3.assert_called_once_with(mock_get_rendered_pages.return_value, "")
    mock_purge_fastly_cache.assert_called_once()
    mock_send_publish_acknowledgement.assert_called_once()


@patch("app.celery.tasks.Alerts.load")
@patch("app.celery.tasks.get_rendered_pages")
@patch("app.celery.tasks.upload_html_to_s3")
@pytest.mark.xfail(raises=Retry)
def test_publish_govuk_alerts_retries(
    mock_upload_to_s3,
    mock_get_rendered_pages,
    mock_Alerts_load,
    govuk_alerts,
):
    mock_upload_to_s3.side_effect = Exception("error")
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
