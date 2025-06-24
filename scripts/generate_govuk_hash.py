
import sys
import hashlib
import base64
from bs4 import BeautifulSoup
import requests


def main():
    govuk_alerts_url = sys.argv[1]
    response = requests.get(govuk_alerts_url)

    html = BeautifulSoup(response.text, 'html.parser')
    body = html.body
    script = body.find_next('script', src=False)
    script_content = script.string.strip()

    hash_digest = hashlib.sha256(script_content.encode("utf-8")).digest()
    return f"sha256-{base64.b64encode(hash_digest).decode('utf-8')}"


main()