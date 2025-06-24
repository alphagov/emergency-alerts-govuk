from flask import Blueprint, Response, current_app

from app.models.alerts import Alerts
from app.render import get_rendered_pages

bp = Blueprint("main", __name__)


@bp.route("/<path:key>", methods=["GET"])
def show_page(key):
    alerts = Alerts.load()
    rendered_pages = get_rendered_pages(alerts)

    if key in rendered_pages:
        if key.endswith(".atom") or key.endswith(".xsl"):
            return Response(rendered_pages[key], mimetype="text/xml")
        else:
            return rendered_pages[key]

    return current_app.send_static_file(key)
