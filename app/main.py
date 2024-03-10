from flask import Blueprint, current_app

from app.models.alerts import Alerts
from app.render import get_rendered_pages

bp = Blueprint('main', __name__)


@bp.route('/<path:key>', methods=['GET'])
def show_page(key):
    alerts = Alerts.load()
    rendered_pages = get_rendered_pages(alerts)

    if key == "alerts.atom":
        ret = Alerts.get_atom_feed()
        print(ret)
        return ret

    if key in rendered_pages:
        return rendered_pages[key]

    return current_app.send_static_file(key)
