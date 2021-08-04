from unittest.mock import patch, ANY

from main import publish_govuk_alerts


@patch('main.alerts_from_yaml')
@patch('main.get_rendered_pages')
@patch('main.upload_to_s3')
@patch('main.purge_cache')
def test_publish_govuk_alerts(
    mock_purge_cache,
    mock_upload_to_s3,
    mock_get_rendered_pages,
    mock_alerts_from_yaml,
):
    publish_govuk_alerts()
    mock_alerts_from_yaml.assert_called_once()
    mock_get_rendered_pages.assert_called_once_with(mock_alerts_from_yaml.return_value)
    mock_upload_to_s3.assert_called_once_with(ANY, mock_get_rendered_pages.return_value)
    mock_purge_cache.assert_called_once()
