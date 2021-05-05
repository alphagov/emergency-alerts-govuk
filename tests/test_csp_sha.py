import base64
import hashlib

from bs4 import BeautifulSoup

from tests.src import env


def test_csp_sha():
    script_sha256_base64_encoded = b"+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU="
    env.filters['file_fingerprint'] = lambda path: path  # stub out filters

    template = env.get_template('src/index.html')
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    inline_script = html.select_one('body > script')

    assert inline_script is not None

    script_code = inline_script.string.strip()

    # generate the sha256 of the script code and base64 encode it
    script_code_sha256 = base64.b64encode(
                                hashlib.sha256(
                                    script_code.encode('utf-8')).digest())

    assert script_code_sha256 == script_sha256_base64_encoded
