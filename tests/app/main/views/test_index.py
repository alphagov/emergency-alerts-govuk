import base64
import hashlib


def test_index_page(client_get):
    html = client_get("alerts")
    assert html.select_one('h1').text.strip() == "Emergency Alerts"
    assert 'current alert' not in html.text


def test_index_page_shows_current_alerts(client_get, mocker, alert_dict):
    mocker.patch('app.models.alerts.Alerts.current_and_public', ['alert'])
    mocker.patch('app.models.alerts.Alerts.last_updated_date')
    html = client_get("alerts")
    assert '1 current alert' in html.text


def test_index_page_content_security_policy_sha(client_get):
    script_sha256_base64_encoded = b"+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU="

    html = client_get("alerts")
    inline_script = html.select_one('body > script')

    assert inline_script is not None
    script_code = inline_script.string.strip()

    # generate the sha256 of the script code and base64 encode it
    script_code_sha256 = base64.b64encode(
        hashlib.sha256(script_code.encode('utf-8')).digest()
    )

    assert script_code_sha256 == script_sha256_base64_encoded