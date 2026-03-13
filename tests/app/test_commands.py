from freezegun import freeze_time


def create_mock_filename(publish_type, publish_origin):
    return f"{publish_type}_{publish_origin}_.txt"


@freeze_time('2026-02-16T11:30:00Z')
def test_publish(mocker, govuk_alerts):
    # This test mocks the invocation of the publish command, via cli, and asserts
    # that mock functions are called with expected arguments
    mock_create_progress = mocker.patch(
        "app.celery.tasks.PublishTaskProgress.create"
    )
    publish_html_mock = mocker.patch('app.commands._publish_html')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    put_success_metric_data_mock = mocker.patch(
        'app.commands.put_success_metric_data'
    )
    runner = govuk_alerts.test_cli_runner()
    runner.invoke(
        args=[
            'publish',
        ]
    )

    publish_html_mock.assert_called_once_with(mock_create_progress.return_value)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    put_success_metric_data_mock.assert_called_once_with('publish-dynamic')


@freeze_time('2026-02-16T11:30:00Z')
def test_startup_publish_with_assets(mocker, govuk_alerts):
    # This test mocks the invocation of the publish-with-assets command, upon startup, and asserts
    # that mock functions are called with expected arguments
    mock_create_progress = mocker.patch(
        "app.celery.tasks.PublishTaskProgress.create"
    )
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    put_success_metric_data_mock = mocker.patch(
        'app.commands.put_success_metric_data'
    )
    runner = govuk_alerts.test_cli_runner()
    runner.invoke(
        args=[
            'publish-with-assets',
            '--startup',  # Passed in within startup script
        ]
    )
    publish_html_mock.assert_called_once_with(mock_create_progress.return_value)
    publish_cap_xml_mock.assert_called_once_with(mock_create_progress.return_value)
    publish_with_assets_mock.assert_called_once_with(mock_create_progress.return_value)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    put_success_metric_data_mock.assert_called_once_with('publish-all')


@freeze_time('2026-02-16T11:30:00Z')
def test_publish_with_assets(mocker, govuk_alerts):
    # This test mocks the invocation of the publish-with-assets command, via cli, and asserts
    # that mock functions are called with expected arguments
    mock_create_progress = mocker.patch(
        "app.celery.tasks.PublishTaskProgress.create"
    )
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    put_success_metric_data_mock = mocker.patch(
        'app.commands.put_success_metric_data'
    )
    runner = govuk_alerts.test_cli_runner()
    runner.invoke(
        args=[
            'publish-with-assets',
        ]
    )

    publish_html_mock.assert_called_once_with(mock_create_progress.return_value)
    publish_cap_xml_mock.assert_called_once_with(mock_create_progress.return_value)
    publish_with_assets_mock.assert_called_once_with(mock_create_progress.return_value)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    put_success_metric_data_mock.assert_called_once_with('publish-all')
