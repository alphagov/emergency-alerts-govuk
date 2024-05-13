import os
from pathlib import Path
from unittest.mock import patch

import boto3
import pytest
from markupsafe import Markup
from moto import mock_aws

from app.utils import (
    capitalise,
    file_fingerprint,
    is_in_uk,
    paragraphize,
    purge_fastly_cache,
    simplify_custom_area_name,
    upload_html_to_s3,
)


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
    client = boto3.client('s3')
    client.create_bucket(Bucket='test-bucket', CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'})

    pages = {"alerts": "<p>this is some test content</p>"}
    upload_html_to_s3(pages)

    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket='test-bucket')['Contents']
    ]

    assert object_keys == ['alerts']

    alerts_object = client.get_object(Bucket='test-bucket', Key='alerts')
    assert alerts_object['Body'].read().decode('utf-8') == pages['alerts']
    assert alerts_object['ContentType'] == 'text/html'


@patch('app.utils.requests')
def test_purge_fastly_cache(mock_requests, govuk_alerts):
    headers = {
        "Accept": "application/json",
        "Fastly-Key": "test-api-key"
    }

    os.environ["FASTLY_SERVICE_ID"] = "test-service-id"
    os.environ["FASTLY_SURROGATE_KEY"] = "test-surrogate-key"
    os.environ['FASTLY_API_KEY'] = "test-api-key"

    purge_fastly_cache()

    fastly_url = "https://api.fastly.com/service/test-service-id/purge/test-surrogate-key"
    mock_requests.post.assert_called_once_with(fastly_url, headers=headers)
    mock_requests.post.return_value.raise_for_status.assert_called_once()
