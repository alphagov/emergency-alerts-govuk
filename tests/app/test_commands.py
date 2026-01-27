def test_publish(mocker, govuk_alerts):
    publish_mock = mocker.patch('app.commands._publish_html')
    runner = govuk_alerts.test_cli_runner()

    runner.invoke(args=['publish'])
    publish_mock.assert_called_once()


def test_publish_with_assets(mocker, govuk_alerts):
    _ = mocker.patch('app.commands._publish_html')
    _ = mocker.patch('app.commands._publish_cap_xml')
    publish_with_assets_mock = mocker.patch('app.commands._publish_assets')
    runner = govuk_alerts.test_cli_runner()

    runner.invoke(args=['publish-with-assets'])
    publish_with_assets_mock.assert_called_once()
