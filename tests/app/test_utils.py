from pathlib import Path
from unittest.mock import patch

import pytest
from jinja2 import Markup

from app.utils import (
    file_fingerprint,
    is_in_uk,
    paragraphize,
    purge_cache,
    upload_to_s3,
)


def test_file_fingerprint_gets_variant_of_path_with_hash_in():
    new_path = file_fingerprint('/tests/test_files/example.txt', root=Path('.'))
    assert new_path == '/tests/test_files/example-4d93d519.txt'


def test_file_fingerprint_raises_for_file_not_found():
    with pytest.raises(OSError):
        file_fingerprint('/tests/test_files/doesnt-exist.txt', root=Path('.'))


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


@patch('app.utils.boto3')
def test_upload_to_s3(mock_boto3):
    config = {
        "BROADCASTS_AWS_ACCESS_KEY_ID": "test-key-id",
        "BROADCASTS_AWS_SECRET_ACCESS_KEY": "test-secret-key",
        "BROADCASTS_AWS_REGION": "test-region-1",
        "GOVUK_ALERTS_S3_BUCKET_NAME": "test-bucket-name"
    }

    pages = {
        "alerts": "<p>this is some test content</p>"
    }

    upload_to_s3(config, pages)

    mock_boto3.session.Session.assert_called_once_with(
        aws_access_key_id=config["BROADCASTS_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=config["BROADCASTS_AWS_SECRET_ACCESS_KEY"],
        region_name=config["BROADCASTS_AWS_REGION"],
    )
    mock_session = mock_boto3.session.Session.return_value

    mock_session.resource.assert_called_once_with('s3')
    mock_s3 = mock_session.resource.return_value

    mock_s3.Object.assert_called_once_with(config['GOVUK_ALERTS_S3_BUCKET_NAME'], 'alerts')
    mock_object = mock_s3.Object.return_value

    mock_object.put.assert_called_once_with(Body=pages['alerts'], ContentType="text/html")


@patch('app.utils.requests')
def test_purge_cache(mock_requests):
    config = {
        "FASTLY_SERVICE_ID": "test-service-id",
        "FASTLY_API_KEY": "test-api-key",
        "FASTLY_SURROGATE_KEY": "test-surrogate-key",
    }

    headers = {
        "Accept": "application/json",
        "Fastly-Key": "test-api-key"
    }

    purge_cache(config)

    fastly_url = "https://api.fastly.com/service/test-service-id/purge/test-surrogate-key"
    mock_requests.post.assert_called_once_with(fastly_url, headers=headers)
    mock_requests.post.return_value.raise_for_status.assert_called_once()
