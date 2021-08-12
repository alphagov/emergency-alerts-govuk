import re
from datetime import datetime
from glob import glob
from pathlib import Path
from urllib.parse import urlparse

import pytest
import pytz
from freezegun import freeze_time

from lib.alerts import Alerts
from tests.conftest import render_template


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
        html = render_template(env, re.sub(r'^\./{1}', '', template_path))
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
        "starts_at": datetime(2021, 4, 21, 11, 25, tzinfo=pytz.utc),
        "approved_at": datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        "cancelled_at": datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc)
    },
    {  # past alert
        "starts_at": datetime(2021, 4, 20, 11, 25, tzinfo=pytz.utc),
        "approved_at": datetime(2021, 4, 20, 11, 30, tzinfo=pytz.utc),
        "cancelled_at": datetime(2021, 4, 20, 12, 30, tzinfo=pytz.utc)
    }
])
@freeze_time(datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc))
def test_local_links_lead_to_existing_routes_in_pages_with_alerts(env, alert_dict, alert_timings):

    # fake an alert existing in the routes and data
    local_routes = local_routes_except_alerts + ['/alerts/21-Apr-2021']
    alert_dict['identifier'] = '21-Apr-2021'

    alert_dict.update(alert_timings)
    alerts_data = Alerts([alert_dict])

    env.globals['alerts'] = alerts_data

    for template_path in all_templates:
        html = render_template(
            env,
            re.sub(r'^\./{1}', '', template_path),
            {'alert_data': alerts_data[0]}
        )
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
    html = render_template(
        env,
        re.sub(r'^\./{1}', '', template_path),
    )
    for link in html.select('main a'):
        assert 'govuk-link' in link['class']


@pytest.mark.parametrize("alert_timings", [
    {  # current alert
        "starts_at": datetime(2021, 4, 21, 11, 25, tzinfo=pytz.utc),
        "approved_at": datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc),
        "cancelled_at": datetime(2021, 4, 21, 12, 30, tzinfo=pytz.utc)
    },
    {  # past alert
        "starts_at": datetime(2021, 4, 20, 11, 25, tzinfo=pytz.utc),
        "approved_at": datetime(2021, 4, 20, 11, 30, tzinfo=pytz.utc),
        "cancelled_at": datetime(2021, 4, 20, 12, 30, tzinfo=pytz.utc)
    }
])
@pytest.mark.parametrize('template_path', all_templates)
@freeze_time(datetime(2021, 4, 21, 11, 30, tzinfo=pytz.utc))
def test_all_pages_with_details_in_have_the_js_for_it(env, alert_dict, alert_timings, template_path):
    alert_dict.update(alert_timings)
    alerts_data = Alerts([alert_dict])

    env.globals['alerts'] = [alerts_data]

    html = render_template(
        env,
        re.sub(r'^\./{1}', '', template_path),
        {'alert_data': alerts_data[0]}
    )
    details = html.select('.govuk-details')

    if len(details) == 0:
        assert True
        return

    assert html.select_one('script[src^="/alerts/assets/javascripts/govuk-frontend-details"]') is not None
