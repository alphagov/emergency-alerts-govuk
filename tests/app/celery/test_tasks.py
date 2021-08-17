from unittest.mock import patch

from app.celery.tasks import publish_govuk_alerts


@patch('app.celery.tasks.Alerts.load')
@patch('app.celery.tasks.get_rendered_pages')
@patch('app.celery.tasks.upload_to_s3')
@patch('app.celery.tasks.purge_cache')
def test_publish_govuk_alerts(
    mock_purge_cache,
    mock_upload_to_s3,
    mock_get_rendered_pages,
    mock_Alerts_load,
):
    publish_govuk_alerts()
    mock_Alerts_load.assert_called_once()
    mock_get_rendered_pages.assert_called_once_with(mock_Alerts_load.return_value)
    mock_upload_to_s3.assert_called_once_with(mock_get_rendered_pages.return_value)
    mock_purge_cache.assert_called_once()
