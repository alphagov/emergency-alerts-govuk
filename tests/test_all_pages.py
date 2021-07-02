import re
from datetime import datetime
from glob import glob
from pathlib import Path
from urllib.parse import urlparse

import pytest
import pytz
from bs4 import BeautifulSoup
from freezegun import freeze_time

from lib.alerts import Alerts


def get_page_html(env, template_path, alert_data=None):
    template = env.get_template(template_path)

    # The file_fingerprint filter accesses the filesystem so mock
    env.filters['file_fingerprint'] = lambda path: path

    if alert_data is not None:
        content = template.render({'alert_data': alert_data})
    else:
        content = template.render()
    return BeautifulSoup(content, 'html.parser')


def get_local_route_from_template_path(template_path):
    local_route = '/alerts/' + Path(template_path).stem
    if local_route != '/alerts/index':
        return local_route
    else:  # index page is mapped to root of /alerts directory
        return '/alerts'


all_templates = glob('./src/*.html')
all_templates_except_alerts = filter(lambda template: template != './src/alert.html', all_templates)
local_routes_except_alerts = [
    get_local_route_from_template_path(template_path)
    for template_path in all_templates]


def test_local_links_lead_to_existing_routes_in_pages_with_no_alerts(env):
    for template_path in all_templates_except_alerts:
        html = get_page_html(env, re.sub(r'^\./{1}', '', template_path))
        local_links = html.select("a[href^='/alerts']")

        # return early if no local links found
        if len(local_links) == 0:
            assert True
            return

        for link in local_links:
            path = urlparse(link['href']).path
            assert path in local_routes_except_alerts


@pytest.mark.parametrize("alert_timings", [
    {  # current alert
        "start": datetime(2021, 4, 21, 11, 25, tzinfo=pytz.utc),
        "sent": datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        "expires": datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc)
    },
    {  # past alert
        "start": datetime(2021, 4, 20, 11, 25, tzinfo=pytz.utc),
        "sent": datetime(2021, 4, 20, 11, 30, tzinfo=pytz.utc),
        "expires": datetime(2021, 4, 20, 12, 30, tzinfo=pytz.utc)
    }
])
@freeze_time(datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc))
def test_local_links_lead_to_existing_routes_in_pages_with_alerts(env, alert_dict, alert_timings):
    alert_dict.update(alert_timings)
    alerts_data = Alerts([alert_dict])

    env.globals['alerts'] = [alerts_data]

    # add route for an alert
    local_routes = local_routes_except_alerts + ['/alerts/21-Apr-2021']

    for template_path in all_templates:
        html = get_page_html(env, re.sub(r'^\./{1}', '', template_path), alerts_data[0])
        local_links = html.select("a[href^='/alerts']")

        # return early if no local links found
        if len(local_links) == 0:
            assert True
            return

        for link in local_links:
            path = urlparse(link['href']).path
            assert path in local_routes


@pytest.mark.parametrize('template_path', all_templates_except_alerts)
def test_links_have_correct_class_attribute(env, alert_dict, template_path):
    html = get_page_html(
        env,
        re.sub(r'^\./{1}', '', template_path),
    )
    for link in html.select('main a'):
        assert 'govuk-link' in link['class']


@pytest.mark.parametrize('template_path', all_templates)
@freeze_time(datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc))
def test_all_pages_with_details_in_have_the_js_for_it(env, alert_dict, template_path):
    current_and_past_alert_timings = [
        {  # current alert
            "start": datetime(2021, 4, 21, 11, 25, tzinfo=pytz.utc),
            "sent": datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
            "expires": datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc)
        },
        {  # past alert
            "start": datetime(2021, 4, 20, 11, 25, tzinfo=pytz.utc),
            "sent": datetime(2021, 4, 20, 11, 30, tzinfo=pytz.utc),
            "expires": datetime(2021, 4, 20, 12, 30, tzinfo=pytz.utc)
        }
    ]

    # add current and past alerts to ensure all pages exist and have content
    for alert_timings in current_and_past_alert_timings:
        alert_dict.update(alert_timings)

    alerts_data = Alerts([alert_dict])
    env.globals['alerts'] = [alerts_data]
    html = get_page_html(env, re.sub(r'^\./{1}', '', template_path), alerts_data[0])
    details = html.select('.govuk-details')

    if len(details) == 0:
        assert True
        return

    assert html.select_one('script[src^="/alerts/assets/javascripts/govuk-frontend-details.js"]') is not None
