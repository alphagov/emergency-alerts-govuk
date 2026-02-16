from pathlib import Path
from unittest.mock import patch

import boto3
import pytest
from flask import current_app
from markupsafe import Markup
from moto import mock_aws

from app.models.alert import Alert
from app.utils import (
    capitalise,
    create_cap_event,
    delete_timestamp_file_from_s3,
    file_fingerprint,
    is_in_uk,
    paragraphize,
    purge_fastly_cache,
    put_success_metric_data,
    put_timestamp_to_s3,
    simplify_custom_area_name,
    upload_html_to_s3,
)
from tests.conftest import create_alert_dict, set_config


def test_file_fingerprint_gets_variant_of_path_with_hash_in():
    new_path = file_fingerprint('/tests/test_files/example.txt', root=Path('.'))
    assert new_path == '/tests/test_files/example-4d93d519.txt'


def test_file_fingerprint_raises_for_file_not_found():
    with pytest.raises(OSError):
        file_fingerprint('/tests/test_files/doesnt-exist.txt', root=Path('.'))


def test_capitalise_capitalises_first_letter():
    text = "this is SoMe TeXt"
    expected = 'This is SoMe TeXt'
    assert capitalise(text) == expected


def test_simplify_simplifies_custom_area_name_in_english():
    postcode_text = "12km around the postcode HU5 5NT, in City of Kingston upon Hull"
    postcode_expected = 'an area in City of Kingston upon Hull'

    cartesian_text = "10km around the easting of 500000.0 and the northing of 180000.0, in Buckinghamshire"
    cartesian_expected = 'an area in Buckinghamshire'

    decimal_text = "10km around 52.14738 latitude, -2.803112 longitude, in County of Herefordshire"
    decimal_expected = 'an area in County of Herefordshire'
    assert simplify_custom_area_name(postcode_text, 'en') == postcode_expected
    assert simplify_custom_area_name(cartesian_text, 'en') == cartesian_expected
    assert simplify_custom_area_name(decimal_text, 'en') == decimal_expected


def test_simplify_simplifies_custom_area_name_in_welsh():
    postcode_text = "12km around the postcode HU5 5NT, in City of Kingston upon Hull"
    postcode_expected = 'ardal yn City of Kingston upon Hull'

    cartesian_text = "10km around the easting of 500000.0 and the northing of 180000.0, in Buckinghamshire"
    cartesian_expected = 'ardal yn Buckinghamshire'

    decimal_text = "10km around 52.14738 latitude, -2.803112 longitude, in County of Herefordshire"
    decimal_expected = 'ardal yn County of Herefordshire'
    assert simplify_custom_area_name(postcode_text, 'cy') == postcode_expected
    assert simplify_custom_area_name(cartesian_text, 'cy') == cartesian_expected
    assert simplify_custom_area_name(decimal_text, 'cy') == decimal_expected


def test_paragraphize_converts_newlines_to_paragraphs():
    lines = 'some\nlines with\n\n&escapes'

    expected = ('<p class="a-class">some</p>\n\n'
                '<p class="a-class">lines with</p>\n\n'
                '<p class="a-class">&amp;escapes</p>')

    assert paragraphize(lines, classes="a-class") == Markup(expected)


@pytest.mark.parametrize('lat,lon,in_uk', [
    [66.55, 25.889, False],  # somewhere in Finland
    [52.22035, 1.58242, True]  # somewhere in UK
])
def test_is_in_uk_returns_polygons_in_uk_bounding_box(alert_dict, lat, lon, in_uk):
    simple_polygons = [[[lat, lon]]]
    assert is_in_uk(simple_polygons) == in_uk


@mock_aws
def test_upload_to_s3(govuk_alerts):
    bucket_name = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    publish_s3_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]

    client = boto3.client('s3')
    client.create_bucket(Bucket=bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': current_app.config["AWS_REGION"]})
    client.create_bucket(Bucket=publish_s3_bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': current_app.config["AWS_REGION"]})

    pages = {"alerts": "<p>this is some test content</p>"}
    upload_html_to_s3(pages, "test")

    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket=bucket_name)['Contents']
    ]

    assert object_keys == ['alerts']

    alerts_object = client.get_object(Bucket=bucket_name, Key='alerts')
    assert alerts_object['Body'].read().decode('utf-8') == pages['alerts']
    assert alerts_object['ContentType'] == 'text/html'


@mock_aws
def test_put_timestamp_to_s3(govuk_alerts):
    publish_s3_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]
    client = boto3.client('s3')
    client.create_bucket(Bucket=publish_s3_bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': current_app.config["AWS_REGION"]})

    task_id = "test-task-id"
    put_timestamp_to_s3(task_id, client)

    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket=publish_s3_bucket_name)['Contents']
    ]

    assert object_keys == [task_id]
    alerts_object = client.get_object(Bucket=publish_s3_bucket_name, Key=task_id)
    assert alerts_object['ContentType'] == 'text/plain'


@mock_aws
def test_cannot_put_timestamp_to_s3_if_missing_bucket_env_var(govuk_alerts):
    # Config env var removed and as its necessary for upload of file to bucket,
    # we can't upload file and we assert that bucket is still empty
    publish_s3_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]
    client = boto3.client('s3')
    client.create_bucket(Bucket=publish_s3_bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': current_app.config["AWS_REGION"]})
    assert client.list_objects_v2(Bucket=publish_s3_bucket_name).get('KeyCount') == 0

    # Setting GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME to None so process returns early and file not uploaded
    with set_config(govuk_alerts, "GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME", None):
        task_id = "test-task-id"
        put_timestamp_to_s3(task_id, client)

    # Still no files in bucket
    assert client.list_objects_v2(Bucket=publish_s3_bucket_name).get('KeyCount') == 0


@mock_aws
def test_delete_timestamp_file_from_s3(govuk_alerts):
    publish_s3_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]
    client = boto3.client('s3')
    client.create_bucket(Bucket=publish_s3_bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': current_app.config["AWS_REGION"]})

    task_id = "test-task-id"
    put_timestamp_to_s3(task_id, client)

    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket=publish_s3_bucket_name)['Contents']
    ]
    assert object_keys == [task_id]
    delete_timestamp_file_from_s3(task_id)
    assert client.list_objects_v2(Bucket=publish_s3_bucket_name).get('KeyCount') == 0


@mock_aws
def test_delete_timestamp_file_returns_early_if_missing_bucket_env_var(govuk_alerts):
    # File is uploaded to bucket, then config env var removed and as its necessary for
    # deletion of file from bucket, we can't delete file and we assert that it remains
    publish_s3_bucket_name = current_app.config["GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME"]
    client = boto3.client('s3')
    client.create_bucket(Bucket=publish_s3_bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': current_app.config["AWS_REGION"]})
    task_id = "test-task-id"
    put_timestamp_to_s3(task_id, client)
    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket=publish_s3_bucket_name)['Contents']
    ]
    assert object_keys == [task_id]

    # Setting GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME to None so process returns early and no deletion
    with set_config(govuk_alerts, "GOVUK_PUBLISH_TIMESTAMPS_S3_BUCKET_NAME", None):
        task_id = "test-task-id"
        delete_timestamp_file_from_s3(task_id)

    # File still remains in bucket
    assert client.list_objects_v2(Bucket=publish_s3_bucket_name).get('KeyCount') == 1


@mock_aws
def test_put_success_metric_data(govuk_alerts):
    client = boto3.client(
        "cloudwatch", region_name=current_app.config["AWS_REGION"]
    )

    origin = "publish-all"
    put_success_metric_data(origin)

    metric = client.list_metrics()["Metrics"][0]
    assert metric["MetricName"] == current_app.config["GOVUK_PUBLISH_METRIC_NAME"]
    assert metric["Namespace"] == current_app.config["GOVUK_PUBLISH_METRIC_NAMESPACE"]
    assert {'Name': 'PublishType', 'Value': origin} in metric["Dimensions"]


@patch('app.utils.requests')
def test_purge_fastly_cache(mock_requests, monkeypatch, govuk_alerts):
    headers = {
        "Accept": "application/json",
        "Fastly-Key": "test-api-key"
    }

    monkeypatch.setenv("FASTLY_SERVICE_ID", "test-service-id")
    monkeypatch.setenv("FASTLY_SURROGATE_KEY", "test-surrogate-key")
    monkeypatch.setenv("FASTLY_API_KEY", "test-api-key")

    purge_fastly_cache()

    fastly_url = "https://api.fastly.com/service/test-service-id/purge/test-surrogate-key"
    mock_requests.post.assert_called_once_with(fastly_url, headers=headers)
    mock_requests.post.return_value.raise_for_status.assert_called_once()


@patch("app.utils.requests")
def test_purge_fastly_cache_disabled(mock_requests, monkeypatch, govuk_alerts):
    with set_config(govuk_alerts, "FASTLY_ENABLED", False):
        purge_fastly_cache()

    mock_requests.post.assert_not_called()


def test_create_cap_event_for_active_alert():
    alert = Alert(create_alert_dict(areas={"simple_polygons": [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]]}))
    assert create_cap_event(alert, alert.id) == {
        'identifier': alert.id,
        'message_type': 'alert',
        'message_format': 'cap',
        'headline': 'GOV.UK Emergency alert',
        'description': alert.content,
        'language': 'en-GB',
        "areas": [
            {
                "polygon": polygons,
            } for polygons in alert.areas.get("simple_polygons")
        ],
        'channel': 'severe',
        'sent': alert.starts_at.isoformat(),
        'expires': alert.finishes_at.isoformat(),  # Expires timestamp is for when the alert is projected to finish
        'web': None
    }


def test_create_cap_event_for_cancelled_alert():
    alert = Alert(create_alert_dict(areas={"simple_polygons": [[[1, 2], [3, 4], [5, 6]],
                                                               [[7, 8], [9, 10], [11, 12]]]}))
    assert create_cap_event(alert, alert.id, cancelled=True) == {
        'identifier': alert.id,
        'message_type': 'alert',
        'message_format': 'cap',
        'headline': 'GOV.UK Emergency alert',
        'description': alert.content,
        'language': 'en-GB',
        'areas': [
            {
                "polygon": polygons,
            } for polygons in alert.areas.get("simple_polygons")
        ],
        'channel': 'severe',
        'sent': alert.starts_at.isoformat(),
        'expires': alert.cancelled_at.isoformat(),  # Expires timestamp is for when the alert was cancelled
        'web': None
    }


@pytest.mark.parametrize('url', [
    "https://www.gov.uk/alerts", None
])
def test_create_cap_event_with_and_without_web_element(url):
    alert = Alert(create_alert_dict(areas={"simple_polygons": [[[1, 2], [3, 4], [5, 6]],
                                                               [[7, 8], [9, 10], [11, 12]]]}))
    assert create_cap_event(alert, alert.id, url=url) == {
        'identifier': alert.id,
        'message_type': 'alert',
        'message_format': 'cap',
        'headline': 'GOV.UK Emergency alert',
        'description': alert.content,
        'language': 'en-GB',
        "areas": [
            {
                "polygon": polygons,
            } for polygons in alert.areas.get("simple_polygons")
        ],
        'channel': 'severe',
        'sent': alert.starts_at.isoformat(),
        'expires': alert.finishes_at.isoformat(),
        'web': url
    }
