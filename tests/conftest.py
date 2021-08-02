from datetime import datetime

import pytest
import pytz
from bs4 import BeautifulSoup

from build import setup_jinja_environment
from lib.alerts import Alerts


@pytest.fixture()
def env():
    test_env = setup_jinja_environment(Alerts([]))
    test_env.filters['file_fingerprint'] = lambda path: path
    return test_env


@pytest.fixture()
def alert_dict():
    return {
        'headline': 'Emergency alert',
        'content': 'Something',
        'general_area_names': [],
        'areas': dict(),
        'channel': 'severe',
        'identifier': '1234',
        'starts_at': datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        'approved_at': datetime(2021, 4, 21, 11, 25, tzinfo=pytz.utc),
        'cancelled_at': datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc),
        'finishes_at': datetime(2021, 4, 21, 15, 30, tzinfo=pytz.utc)
    }


def render_template(env, template_path, template_vars={}):
    template = env.get_template(template_path)
    content = template.render(template_vars)
    return BeautifulSoup(content, 'html.parser')
