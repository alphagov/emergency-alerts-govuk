from freezegun import freeze_time


def create_mock_filename(publish_type, publish_origin):
    task_id = "taskid"
    timestamp = "1771241400"
    return f"{publish_type}_{publish_origin}_{task_id}_{timestamp}.txt"


@freeze_time('2026-02-16T11:30:00Z')
def test_publish(mocker, govuk_alerts, mock_get_ecs_task_id):
    # This test mocks the invocation of the publish command, via cli, and asserts
    # that mock functions are called with expected arguments
    filename = create_mock_filename("publish-dynamic", "cli")

    publish_html_mock = mocker.patch('app.commands._publish_html')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    delete_timestamp_file_mock = mocker.patch(
        'app.commands.delete_timestamp_file_from_s3'
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

    publish_html_mock.assert_called_once_with(filename)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    delete_timestamp_file_mock.assert_called_once_with(filename)
    put_success_metric_data_mock.assert_called_once_with('publish-dynamic')


@freeze_time('2026-02-16T11:30:00Z')
def test_startup_publish_with_assets(mocker, govuk_alerts, mock_get_ecs_task_id):
    # This test mocks the invocation of the publish-with-assets command, upon startup, and asserts
    # that mock functions are called with expected arguments
    filename = create_mock_filename("publish-all", "startup")
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    delete_timestamp_file_mock = mocker.patch(
        'app.commands.delete_timestamp_file_from_s3'
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
    publish_html_mock.assert_called_once_with(filename)
    publish_cap_xml_mock.assert_called_once_with(filename)
    publish_with_assets_mock.assert_called_once_with(filename)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    delete_timestamp_file_mock.assert_called_once_with(filename)
    put_success_metric_data_mock.assert_called_once_with('publish-all')


@freeze_time('2026-02-16T11:30:00Z')
def test_publish_with_assets(mocker, govuk_alerts, mock_get_ecs_task_id):
    # This test mocks the invocation of the publish-with-assets command, via cli, and asserts
    # that mock functions are called with expected arguments
    filename = create_mock_filename("publish-all", "cli")
    publish_html_mock = mocker.patch('app.commands._publish_html')
    publish_cap_xml_mock = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    purge_fastly_cache_mock = mocker.patch('app.commands.purge_fastly_cache')
    send_publish_ack_mock = mocker.patch(
        'app.commands.alerts_api_client.send_publish_acknowledgement'
    )
    delete_timestamp_file_mock = mocker.patch(
        'app.commands.delete_timestamp_file_from_s3'
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

    publish_html_mock.assert_called_once_with(filename)
    publish_cap_xml_mock.assert_called_once_with(filename)
    publish_with_assets_mock.assert_called_once_with(filename)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()
    delete_timestamp_file_mock.assert_called_once_with(filename)
    put_success_metric_data_mock.assert_called_once_with('publish-all')


@freeze_time('2026-02-16T11:30:00Z')
def test_publish_fails_without_args(mocker, govuk_alerts):
    # This test mocks the invocation of the publish command, and the
    # return value when `get_ecs_task_id` is unable to source ECS Task ID,
    # and then asserts that functions are called, and not called in this instance,
    # with expected arguments
    mock_get_ecs_task_id = mocker.patch("app.utils.get_ecs_task_id")
    mock_get_ecs_task_id.side_effect = Exception("No ECS task id")

    publish_html_mock = mocker.patch("app.commands._publish_html")
    purge_fastly_cache_mock = mocker.patch("app.commands.purge_fastly_cache")
    send_publish_ack_mock = mocker.patch(
        "app.commands.alerts_api_client.send_publish_acknowledgement"
    )
    delete_timestamp_file_mock = mocker.patch(
        "app.commands.delete_timestamp_file_from_s3"
    )
    put_success_metric_data_mock = mocker.patch(
        "app.commands.put_success_metric_data"
    )

    runner = govuk_alerts.test_cli_runner()
    runner.invoke(args=["publish"])

    publish_html_mock.assert_called_once_with(None)
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()

    # The following mocks haven't been called because the args weren't provided with
    # command, so no filename means we can't delete the file or declare the publish
    # successful
    delete_timestamp_file_mock.assert_not_called()
    put_success_metric_data_mock.assert_not_called()
