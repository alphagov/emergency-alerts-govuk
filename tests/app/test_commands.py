def test_publish(mocker, govuk_alerts):
    publish_mock = mocker.patch('app.commands.publish_govuk_alerts')
    runner = govuk_alerts.test_cli_runner()

    runner.invoke(args=['publish'])
    publish_mock.assert_called_once()
