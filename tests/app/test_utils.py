import io
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import boto3
import botocore
import pytest
from flask import current_app
from markupsafe import Markup
from moto import mock_aws

from app.models.alert import Alert
from app.utils import (
    _get_latest_govuk_archive,
    _get_mime_type,
    archive_website,
    capitalise,
    create_cap_event,
    file_fingerprint,
    get_publish_destination,
    is_in_uk,
    paragraphize,
    prepare_destination,
    purge_fastly_cache,
    restore_latest_archive,
    simplify_custom_area_name,
    switch_destination,
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


@pytest.mark.parametrize('malicious_content', [
    '<script>alert("xss")</script>',
    '<img src=x onerror=alert(1)>',
    '<a href="javascript:alert(1)">click</a>',
    '"><svg onload=alert(1)>',
    '"><script>alert(document.cookie)</script>',
])
def test_paragraphize_escapes_html(malicious_content):
    result = paragraphize(malicious_content)
    assert '<script>' not in result
    assert '<img ' not in result
    assert '<a ' not in result
    assert '<svg ' not in result
    assert '&lt;' in result


@pytest.mark.parametrize('malicious_content', [
    '<script>alert("xss")</script>',
    '<img src=x onerror=alert(1)>',
    '<a href="javascript:alert(1)">click</a>',
])
def test_paragraphize_truncated_escapes_html(malicious_content):
    result = paragraphize(malicious_content, truncate=True)
    assert '<script>' not in result
    assert '<img ' not in result
    assert '<a ' not in result
    assert '&lt;' in result


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

    client = boto3.client("s3")
    _ensure_bucket(client, bucket_name)

    pages = {"alerts": "<p>this is some test content</p>"}
    upload_html_to_s3(pages, bucket_name)

    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket=bucket_name)['Contents']
    ]

    assert 'alerts' in object_keys

    alerts_object = client.get_object(Bucket=bucket_name, Key='alerts')
    assert alerts_object['Body'].read().decode('utf-8') == pages['alerts']
    assert alerts_object['ContentType'] == 'text/html'


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
    alert = Alert(
        create_alert_dict(areas={
            "simple_polygons": [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]],
            "aggregate_names": ["England", "Scotland", "Wales"]
        }))
    assert create_cap_event(alert, alert.id) == {
        'identifier': alert.id,
        'message_type': 'alert',
        'message_format': 'cap',
        'headline': 'GOV.UK Emergency alert',
        'description': alert.content,
        'language': 'en',
        "areas": [
            {
                "polygons": [
                    polygons for polygons in alert.areas.get("simple_polygons")
                ],
                "description": alert.display_areas_formatted_string
            },
        ],
        'channel': 'severe',
        'sent': alert.starts_at.isoformat(),
        'expires': alert.finishes_at.isoformat(),  # Expires timestamp is for when the alert is projected to finish
        'web': None
    }


def test_create_cap_event_for_cancelled_alert():
    alert = Alert(create_alert_dict(areas={"simple_polygons": [[[1, 2], [3, 4], [5, 6]],
                                                               [[7, 8], [9, 10], [11, 12]]]}))
    assert create_cap_event(alert, alert.id, cancelled=True, prev_alert_identifier=alert.id) == {
        'identifier': alert.id,
        'message_type': 'cancel',
        'message_format': 'cap',
        'headline': 'GOV.UK Emergency alert',
        'description': alert.content,
        'language': 'en',
        'areas': [
            {
                "polygons": [
                    polygons for polygons in alert.areas.get("simple_polygons")
                ]
            }
        ],
        'channel': 'severe',
        'sent': alert.starts_at.isoformat(),
        'expires': alert.cancelled_at.isoformat(),  # Expires timestamp is for when the alert was cancelled
        'web': None,
        'references': [
            {
                'message_id': alert.id,
                'sent': alert.starts_at.isoformat()
            }
        ]
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
        'language': 'en',
        "areas": [
            {
                "polygons": [
                    polygons for polygons in alert.areas.get("simple_polygons")
                    ]
            }
        ],
        'channel': 'severe',
        'sent': alert.starts_at.isoformat(),
        'expires': alert.finishes_at.isoformat(),
        'web': url
    }


@mock_aws
def test_archive_website(govuk_alerts):
    source_bucket = current_app.config["GOVUK_ALERTS_S3_BUCKET_NAME"]
    dest_bucket = current_app.config["GOVUK_ALERTS_ARCHIVE_S3_BUCKET_NAME"]

    client = boto3.client("s3", region_name="eu-west-2")

    _ensure_bucket(client, source_bucket)
    _ensure_bucket(client, dest_bucket)

    # Create test content
    pages = {"alerts": "<p>this is some test content</p>"}
    upload_html_to_s3(pages, source_bucket)
    capxml = {"alert.cap.xml": "<p>this is some test content</p>"}
    upload_html_to_s3(capxml, source_bucket)

    # Archive it
    archive_website(html=pages, capxml=capxml)

    # Check archive exists
    object_keys = [
        obj['Key'] for obj in
        client.list_objects(Bucket=dest_bucket)['Contents']
    ]
    assert len(object_keys) == 1
    assert object_keys[0] == 'archive_govuk-alerts-website.tar.gz'

    # Check archive includes the file uploaded
    obj = client.get_object(Bucket=dest_bucket, Key=object_keys[0])
    body = obj["Body"].read()

    tar_bytes = io.BytesIO(body)

    with tarfile.open(fileobj=tar_bytes, mode="r:gz") as tar:
        names = tar.getnames()

    assert "alerts.html" in names
    assert "alert.cap.xml" in names


def _ensure_bucket(client, bucket_name, region="eu-west-2"):
    try:
        client.head_bucket(Bucket=bucket_name)
        # Bucket exists, nothing to do
        return
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code != 404:
            raise  # Something else went wrong

    # Bucket does not exist → create it
    client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region},
    )


@pytest.mark.parametrize(
    "ssm_value, expected, exception",
    [
        ("blue",  "green-bucket", None),
        ("green", "blue-bucket",  None),
        ("purple", None, ValueError),
        (Exception("boom"), None, RuntimeError),
    ],
)
@patch("app.utils.setup_ssm_session")
def test_get_publish_destination(
    mock_ssm, monkeypatch, govuk_alerts, ssm_value, expected, exception
):
    monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_CURRENT_BUCKET_PARAM", "alerts-current")
    monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_BLUE_S3_BUCKET_NAME", "blue-bucket")
    monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_GREEN_S3_BUCKET_NAME", "green-bucket")

    ssm = MagicMock()
    mock_ssm.return_value = ssm

    if isinstance(ssm_value, Exception):
        ssm.get_parameter.side_effect = ssm_value
    else:
        ssm.get_parameter.return_value = {"Parameter": {"Value": ssm_value}}

    if exception:
        with pytest.raises(exception):
            get_publish_destination()
    else:
        assert get_publish_destination() == expected


@patch("app.utils.setup_s3_session")
def test_prepare_destination_deletes_all_objects(mock_s3_session):
    s3 = MagicMock()
    mock_s3_session.return_value = s3

    paginator = MagicMock()
    s3.get_paginator.return_value = paginator

    paginator.paginate.return_value = [
        {"Contents": [{"Key": f"file{i}"} for i in range(3)]},
        {"Contents": [{"Key": f"file{i}"} for i in range(3, 5)]},
    ]

    prepare_destination("my-bucket")

    # Only ONE delete call because total < 1000
    s3.delete_objects.assert_called_once_with(
        Bucket="my-bucket",
        Delete={"Objects": [
            {"Key": "file0"},
            {"Key": "file1"},
            {"Key": "file2"},
            {"Key": "file3"},
            {"Key": "file4"},
        ]}
    )


@pytest.mark.parametrize(
    "members, contents, mime_types, expected",
    [
        (
            # members
            ["alerts.html", "foo/bar.txt"],
            # contents
            [b"<html>content</html>", b"hello world"],
            # mime types
            ["text/html", "text/plain"],
            # expected upload list
            [
                {"key": "alerts", "data": b"<html>content</html>", "content_type": "text/html"},
                {"key": "foo/bar.txt", "data": b"hello world", "content_type": "text/plain"},
            ],
        ),
        (
            ["index.html"],
            [b"hi"],
            ["text/html"],
            [
                {"key": "index.html", "data": b"hi", "content_type": "text/html"},
            ],
        ),
    ],
)
@patch("app.utils._upload_files_threaded")
@patch("app.utils._get_mime_type")
@patch("app.utils._get_latest_govuk_archive")
@patch("app.utils.setup_s3_session")
@patch("app.utils.tarfile.open")
def test_restore_latest_archive_success(
    mock_tar_open,
    mock_setup_s3,
    mock_get_latest,
    mock_get_mime,
    mock_upload_threaded,
    members,
    contents,
    mime_types,
    expected,
):
    s3 = MagicMock()
    mock_setup_s3.return_value = s3

    mock_get_latest.return_value = ("ts", MagicMock())

    tar = MagicMock()
    mock_tar_open.return_value.__enter__.return_value = tar

    # Build fake tar members
    fake_members = []
    for name in members:
        m = MagicMock()
        m.name = name
        m.isfile.return_value = True
        fake_members.append(m)

    tar.getmembers.return_value = fake_members

    # Fake extractfile() results
    extracted_files = []
    for content in contents:
        ef = MagicMock()
        ef.read.return_value = content
        extracted_files.append(ef)

    tar.extractfile.side_effect = extracted_files

    # Fake MIME types
    mock_get_mime.side_effect = mime_types

    restore_latest_archive("bucket")

    mock_upload_threaded.assert_called_once()
    uploaded = mock_upload_threaded.call_args.args[2]

    assert uploaded == expected


@pytest.mark.parametrize("dir_name", ["folder/", "nested/dir/", "assets/"])
@patch("app.utils._upload_files_threaded")
@patch("app.utils._get_latest_govuk_archive")
@patch("app.utils.setup_s3_session")
@patch("app.utils.tarfile.open")
def test_restore_latest_archive_skips_non_files(
    mock_tar_open,
    mock_setup_s3,
    mock_get_latest,
    mock_upload_threaded,
    dir_name,
):
    s3 = MagicMock()
    mock_setup_s3.return_value = s3

    mock_get_latest.return_value = ("ts", MagicMock())

    tar = MagicMock()
    mock_tar_open.return_value.__enter__.return_value = tar

    member = MagicMock()
    member.name = dir_name
    member.isfile.return_value = False

    tar.getmembers.return_value = [member]

    restore_latest_archive("bucket")

    mock_upload_threaded.assert_called_once_with(s3, "bucket", [])


@pytest.mark.parametrize(
    "member_name, error",
    [
        ("badfile.txt", Exception("boom")),
        ("alerts.html", IOError("read error")),
    ],
)
@patch("app.utils._get_latest_govuk_archive")
@patch("app.utils.setup_s3_session")
@patch("app.utils.tarfile.open")
def test_restore_latest_archive_raises_runtime_error(
    mock_tar_open,
    mock_setup_s3,
    mock_get_latest,
    member_name,
    error,
):
    s3 = MagicMock()
    mock_setup_s3.return_value = s3

    mock_get_latest.return_value = ("ts", MagicMock())

    tar = MagicMock()
    mock_tar_open.return_value.__enter__.return_value = tar

    member = MagicMock()
    member.name = member_name
    member.isfile.return_value = True

    tar.getmembers.return_value = [member]

    tar.extractfile.side_effect = error

    with pytest.raises(RuntimeError) as exc:
        restore_latest_archive("bucket")

    msg = str(exc.value)
    assert member_name in msg
    assert str(error) in msg


@pytest.mark.parametrize(
    "name, expected",
    [
        # Special cases
        ("foo.cap.xml", "application/cap+xml"),
        ("alert.atom", "text/xml"),
        ("index.cy", "text/html"),
        ("template.xsl", "text/html"),

        # No extension → default to text/html
        ("alerts", "text/html"),

        # Known extensions from mimetype_from_extension
        ("image.png", "image/png"),
        ("photo.jpg", "image/jpeg"),
        ("icon.ico", "image/x-icon"),
        ("script.js", "application/javascript"),
        ("style.css", "text/css"),
        ("font.woff", "font/woff"),
        ("font.woff2", "font/woff2"),
        ("vector.svg", "image/svg+xml"),
        ("image.webp", "image/webp"),

        # Unknown extension → fallback to application/octet-stream
        ("file.unknownext", "application/octet-stream"),
    ],
)
def test_get_mime_type(name, expected):
    assert _get_mime_type(name) == expected


@pytest.mark.parametrize(
    "bucket_config, "
    "head_response, "
    "body_bytes, "
    "head_side_effect, "
    "get_side_effect, "
    "expected_exception, "
    "expected_timestamp_type",
    [
        # SUCCESS: timestamp is datetime
        (
            "archive-bucket",
            {"LastModified": datetime(2024, 1, 1, tzinfo=timezone.utc)},
            b"fake-archive",
            None,
            None,
            None,
            datetime,
        ),

        # SUCCESS: timestamp is string → parsed
        (
            "archive-bucket",
            {"LastModified": "2024-01-01T00:00:00Z"},
            b"fake-archive",
            None,
            None,
            None,
            datetime,
        ),

        # FAILURE: bucket not configured
        (
            "",
            None,
            None,
            None,
            None,
            RuntimeError,
            None,
        ),

        # FAILURE: head_object blows up
        (
            "archive-bucket",
            None,
            None,
            Exception("boom"),
            None,
            RuntimeError,
            None,
        ),

        # FAILURE: get_object blows up
        (
            "archive-bucket",
            {"LastModified": datetime(2024, 1, 1, tzinfo=timezone.utc)},
            None,
            None,
            Exception("read-fail"),
            RuntimeError,
            None,
        ),
    ],
)
@patch("app.utils.setup_s3_session")
@patch("app.utils.dt_parse")
def test_get_latest_govuk_archive(
    mock_dt_parse,
    mock_setup_s3,
    govuk_alerts,
    bucket_config,
    head_response,
    body_bytes,
    head_side_effect,
    get_side_effect,
    expected_exception,
    expected_timestamp_type,
):
    # Enter Flask app context
    with govuk_alerts.app_context():
        # Patch config
        govuk_alerts.config["GOVUK_ALERTS_ARCHIVE_S3_BUCKET_NAME"] = bucket_config

        # Fake S3 client
        s3 = MagicMock()
        mock_setup_s3.return_value = s3

        # head_object behaviour
        if head_side_effect:
            s3.head_object.side_effect = head_side_effect
        elif head_response:
            s3.head_object.return_value = head_response

        # get_object behaviour
        if get_side_effect:
            s3.get_object.side_effect = get_side_effect
        elif body_bytes is not None:
            s3.get_object.return_value = {"Body": io.BytesIO(body_bytes)}

        # dt_parse behaviour
        mock_dt_parse.return_value = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Assertions
        if expected_exception:
            with pytest.raises(expected_exception):
                _get_latest_govuk_archive(s3)
        else:
            timestamp, archive = _get_latest_govuk_archive(s3)

            assert isinstance(timestamp, expected_timestamp_type)
            assert isinstance(archive, io.BytesIO)
            assert archive.read() == body_bytes


@pytest.mark.parametrize(
    "switch_to, cf_enabled, expected_preview_call, expected_prod_call, expected_param",
    [
        # --- SWITCH TO BLUE ---
        (
            "blue-bucket", True,
            ("preview-id", "green-bucket"),   # preview → green
            ("prod-id", "blue-bucket"),       # prod → blue
            "blue",
        ),
        (
            "blue-bucket", False,
            None,  # no CloudFront calls
            None,
            "blue",
        ),

        # --- SWITCH TO GREEN ---
        (
            "green-bucket", True,
            ("preview-id", "blue-bucket"),    # preview → blue
            ("prod-id", "green-bucket"),      # prod → green
            "green",
        ),
        (
            "green-bucket", False,
            None,
            None,
            "green",
        ),
    ],
)
@patch("app.utils._update_current_bucket_parameter")
@patch("app.utils._update_cf_origin")
@patch("app.utils.boto3.client")
def test_switch_destination(
    mock_boto_client,
    mock_update_cf_origin,
    mock_update_param,
    govuk_alerts,
    monkeypatch,
    switch_to,
    cf_enabled,
    expected_preview_call,
    expected_prod_call,
    expected_param,
):
    # --- Setup Flask config ---
    with govuk_alerts.app_context():
        monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_CLOUDFRONT_ENABLED", cf_enabled)
        monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_CLOUDFRONT_ID", "prod-id")
        monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_CLOUDFRONT_ID_PREVIEW", "preview-id")
        monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_BLUE_S3_BUCKET_NAME", "blue-bucket")
        monkeypatch.setitem(govuk_alerts.config, "GOVUK_ALERTS_GREEN_S3_BUCKET_NAME", "green-bucket")

        # Fake CloudFront client
        mock_cf = MagicMock()
        mock_boto_client.return_value = mock_cf

        # --- Execute ---
        switch_destination(switch_to)

        # --- Assertions ---
        if expected_preview_call:
            mock_update_cf_origin.assert_any_call(
                mock_cf,
                expected_preview_call[0],
                expected_preview_call[1],
            )
        else:
            mock_update_cf_origin.assert_not_called()

        if expected_prod_call:
            mock_update_cf_origin.assert_any_call(
                mock_cf,
                expected_prod_call[0],
                expected_prod_call[1],
            )

        # Always update SSM parameter
        mock_update_param.assert_called_once_with(expected_param)
