import hmac
import logging
import os

from flask import Blueprint, Flask, current_app, jsonify
from flask_httpauth import HTTPBasicAuth

from build import alerts_from_api, get_rendered_pages
from lib.utils import purge_cache, upload_to_s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
main = Blueprint('main', __name__)
auth = HTTPBasicAuth()

credentials = {
    "notify-api": os.getenv('NOTIFY_API_SHARED_KEY', 'TestPass')
}


@auth.verify_password
def verify_password(username, password):
    credentials = current_app.config['CREDENTIALS']
    if username in credentials and hmac.compare_digest(credentials[username], password):
        return username


@main.route('/refresh-alerts', methods=['POST'])
@auth.login_required
def refresh_alerts():
    alerts = alerts_from_api()
    rendered_pages = get_rendered_pages(alerts)

    upload_to_s3(rendered_pages)

    purge_cache()
    return jsonify(success=True)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    return app


app = create_app()
