def test_publish(mocker, govuk_alerts):
    current_timestamp = 1770982557
    container_id = 'container_id'
    publish_healthcheck_filename = f"{container_id}_{current_timestamp}"

    publish_mock = mocker.patch('app.commands._publish_html')
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

    runner.invoke(args=[
            'publish',
            '--container-id',
            container_id,
            '--current-timestamp',
            current_timestamp,
        ])
    publish_mock.assert_called_once_with(publish_healthcheck_filename)
    purge_fastly_cache_mock.assert_called_once_with()
    send_publish_ack_mock.assert_called_once_with()
    delete_timestamp_file_mock.assert_called_once_with(publish_healthcheck_filename)
    put_success_metric_data_mock.assert_called_once_with('publish-dynamic')


def test_publish_with_assets(mocker, govuk_alerts):
    current_timestamp = 1770982557
    container_id = 'container_id'
    publish_healthcheck_filename = f"{container_id}_{current_timestamp}"

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
            '--container-id',
            container_id,
            '--current-timestamp',
            current_timestamp,
        ]
    )

    publish_html_mock.assert_called_once_with(publish_healthcheck_filename)
    publish_cap_xml_mock.assert_called_once_with(publish_healthcheck_filename)
    publish_with_assets_mock.assert_called_once_with(publish_healthcheck_filename)
    purge_fastly_cache_mock.assert_called_once_with()
    send_publish_ack_mock.assert_called_once_with()
    delete_timestamp_file_mock.assert_called_once_with(publish_healthcheck_filename)
    put_success_metric_data_mock.assert_called_once_with('publish-all')


def test_publish_fails_without_args(mocker, govuk_alerts):
    publish_mock = mocker.patch('app.commands._publish_html')
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

    runner.invoke(args=[
            'publish'
        ])
    publish_mock.assert_called_once()
    purge_fastly_cache_mock.assert_called_once()
    send_publish_ack_mock.assert_called_once()

    # The following mocks haven't been called because the args weren't provided with
    # command so no filename means we can't delete the file or declare publish
    # successful as publish healthcheck requires files to be published
    delete_timestamp_file_mock.assert_not_called()
    put_success_metric_data_mock.assert_not_called()
