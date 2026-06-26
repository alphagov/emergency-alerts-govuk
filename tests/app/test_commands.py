from freezegun import freeze_time


def create_mock_filename(publish_type, publish_origin):
    return f"{publish_type}_{publish_origin}_123"


@freeze_time('2026-02-16T11:30:00Z')
def test_publish(mocker, govuk_alerts):
    # This test mocks the invocation of the publish command, via cli, and asserts
    # that mock functions are called with expected arguments
    mock_get_publish_destination = mocker.patch("app.commands.get_publish_destination")
    mock_prepare_destination = mocker.patch("app.commands.prepare_destination")
    mock_restore_latest_archive = mocker.patch("app.commands.restore_latest_archive")
    mock_create_progress = mocker.patch("app.tasks.tasks.PublishTaskProgress.create")
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    mock_switch_destination = mocker.patch('app.commands.switch_destination')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    archive_website_mock = mocker.patch('app.commands.archive_website')
    runner = govuk_alerts.test_cli_runner()
    runner.invoke(
        args=[
            'publish',
        ]
    )

    mock_get_publish_destination.assert_called_once()
    mock_prepare_destination.assert_called_once_with(mock_get_publish_destination.return_value)
    mock_restore_latest_archive.assert_called_once_with(mock_get_publish_destination.return_value)
    publish_html_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    publish_cap_xml_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    mock_switch_destination.assert_called_once_with(mock_get_publish_destination.return_value)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    archive_website_mock.assert_called_once()


@freeze_time('2026-02-16T11:30:00Z')
def test_startup_publish_with_assets(mocker, govuk_alerts):
    # This test mocks the invocation of the publish-with-assets command, upon startup, and asserts
    # that mock functions are called with expected arguments
    mock_get_publish_destination = mocker.patch("app.commands.get_publish_destination")
    mock_prepare_destination = mocker.patch("app.commands.prepare_destination")
    mock_restore_latest_archive = mocker.patch("app.commands.restore_latest_archive")
    mock_create_progress = mocker.patch("app.tasks.tasks.PublishTaskProgress.create")
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    archive_website_mock = mocker.patch('app.commands.archive_website')
    runner = govuk_alerts.test_cli_runner()
    runner.invoke(
        args=[
            'publish-with-assets',
            '--startup',  # Passed in within startup script
        ]
    )
    mock_get_publish_destination.assert_called_once()
    mock_prepare_destination.assert_called_once_with(mock_get_publish_destination.return_value)
    mock_restore_latest_archive.assert_called_once_with(mock_get_publish_destination.return_value)
    publish_html_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    publish_cap_xml_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    publish_with_assets_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    archive_website_mock.assert_called_once()


@freeze_time('2026-02-16T11:30:00Z')
def test_publish_with_assets(mocker, govuk_alerts):
    # This test mocks the invocation of the publish-with-assets command, via cli, and asserts
    # that mock functions are called with expected arguments
    mock_get_publish_destination = mocker.patch("app.commands.get_publish_destination")
    mock_prepare_destination = mocker.patch("app.commands.prepare_destination")
    mock_restore_latest_archive = mocker.patch("app.commands.restore_latest_archive")
    mock_create_progress = mocker.patch("app.tasks.tasks.PublishTaskProgress.create")
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    archive_website_mock = mocker.patch('app.commands.archive_website')
    runner = govuk_alerts.test_cli_runner()
    runner.invoke(
        args=[
            'publish-with-assets',
        ]
    )
    mock_get_publish_destination.assert_called_once()
    mock_prepare_destination.assert_called_once_with(mock_get_publish_destination.return_value)
    mock_restore_latest_archive.assert_called_once_with(mock_get_publish_destination.return_value)
    publish_html_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    publish_cap_xml_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    publish_with_assets_mock.assert_called_once_with(
        mock_create_progress.return_value,
        mock_get_publish_destination.return_value
    )
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    archive_website_mock.assert_called_once()
