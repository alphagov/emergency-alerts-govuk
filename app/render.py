from emergency_alerts_utils.formatters import autolink_urls, formatted_list
from feedgen.feed import FeedGenerator
from flask import current_app
from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
    pass_context,
)

from app.utils import (
    DIST,
    REPO,
    capitalise,
    file_fingerprint,
    paragraphize,
    simplify_custom_area_name,
)

TEMPLATES = REPO / 'app' / 'templates'
VIEWS = TEMPLATES / 'views'

all_view_paths = [
    str(path.relative_to(VIEWS)) for path in VIEWS.glob('*.html')
]


@pass_context
def jinja_filter_get_url_for_alert(jinja_context, alert):
    alerts = jinja_context['alerts']
    return get_url_for_alert(alert, alerts)


def get_url_for_alert(alert, alerts):
    """
    Gets the url slug for an alert (given the global alerts object obtained from `Alerts.load()`.)

    Note: The alert must be public to have a url slug.

    Will return a date string in the style '3-jun-2021', unless there were already alerts that day, in which case it'll
    append a 1-indexed counter on to the end eg '3-jun-2021-2'. Note that the first alert of the day never has a count.
    """
    alerts_on_this_day = sorted([
        other_alert
        for other_alert in alerts.public
        if other_alert.starts_at_date.as_local_date == alert.starts_at_date.as_local_date
    ])

    if not alerts_on_this_day:
        raise ValueError(f'Alert {alert.id} is not public so does not have a URL')

    # if this is the first alert of the day (or the only alert of the day), then don't include a counter
    if alert == alerts_on_this_day[0]:
        return alert.starts_at_date.as_url

    # count through the alerts that day til we find this one, so we know
    for i, other_alert in enumerate(alerts_on_this_day[1:], start=2):
        if alert == other_alert:
            return f'{alert.starts_at_date.as_url}-{i}'
    raise ValueError(f'Couldnt find alert {alert.id} in public alerts for day')


def setup_jinja_environment(alerts):
    jinja_loader = ChoiceLoader([
        FileSystemLoader(str(TEMPLATES)),
        FileSystemLoader(str(VIEWS)),
        PrefixLoader({
            'govuk_frontend_jinja': PackageLoader('govuk_frontend_jinja')
        })
    ])

    env = Environment(loader=jinja_loader, autoescape=True)
    env.filters['autolink_urls'] = autolink_urls
    env.filters['file_fingerprint'] = file_fingerprint
    env.filters['formatted_list'] = formatted_list
    env.filters['paragraphize'] = paragraphize
    env.filters['capitalise'] = capitalise
    env.filters['get_url_for_alert'] = jinja_filter_get_url_for_alert
    env.filters['simplify_custom_area_name'] = simplify_custom_area_name
    env.globals = {
        'font_paths': [
            item.relative_to(DIST)
            for item in DIST.glob('alerts/assets/fonts/*.woff2')
        ],
        'alerts': alerts,
    }

    return env


def get_rendered_pages(alerts):
    env = setup_jinja_environment(alerts)
    rendered = {}

    fg = _get_feed_generator()
    feed_item_count = 0

    for path in all_view_paths:
        template = env.get_template(path)
        target = path.replace(".html", "")

        # render each individual alert's page
        if target == 'alert':
            for alert in alerts.public:
                alert_url = get_url_for_alert(alert, alerts)
                rendered["alerts/" + alert_url] = template.render({'alert_data': alert})
                if feed_item_count < 20:
                    _add_feed_entry(fg, alert, alert_url)
                    feed_item_count += 1
            continue

        # Render each alert's page in Welsh
        if target == 'alert.cy':
            for alert in alerts.public:
                alert_url = get_url_for_alert(alert, alerts)
                rendered["alerts/" + alert_url + ".cy"] = template.render({'alert_data': alert})
            continue

        if target == 'index':
            rendered['alerts'] = template.render()
            continue

        if target == 'index.cy':
            rendered['alerts/about.cy'] = template.render()
            continue

        rendered["alerts/" + target] = template.render()

    rendered['alerts/atom'] = fg.atom_str(pretty=True)

    return rendered


def _get_feed_generator():

    host_url = current_app.config["HOST_URL"]

    fg = FeedGenerator()
    fg.id(f"{host_url}/alerts/atom")
    fg.title("GOV.UK Emergency Alerts Service")
    fg.author(name="Emergency Alerts Service", uri="https://www.gov.uk/contact/govuk")
    fg.link(
        href=f"{host_url}/alerts/atom",
        rel="self",
        hreflang="en",
        title="Emergency Alerts Feed"
    )
    icon_file = file_fingerprint("/alerts/assets/images/favicon.ico")
    # fg.icon(icon=f"{host_url}{icon_file}")
    fg.icon(icon=icon_file)
    logo_file = file_fingerprint("/alerts/assets/images/govuk-opengraph-image.png")
    # fg.logo(logo=f"{host_url}{logo_file}")
    fg.logo(logo=logo_file)
    fg.subtitle("Emergency Alerts Feed")
    fg.language("en")
    fg.rights(
        "Released under the Open Government Licence (OGL), "
        "citation of publisher and online resource required on reuse."
    )

    return fg


def _add_feed_entry(fg, alert, alert_url):

    host_url = current_app.config["HOST_URL"]

    title = alert_url
    if alert.areas.get("aggregate_names"):
        title = ", ".join(alert.areas["aggregate_names"])
    else:
        title = ", ".join(alert.areas["names"])

    fe = fg.add_entry()
    fe.id(f"{host_url}/alerts/" + alert_url)
    fe.title(title)
    fe.updated(alert.cancelled_at if alert.is_past else alert.approved_at)
    fe.author(name="Emergency Alerts Service", uri="https://www.gov.uk/contact/govuk")
    fe.content(alert.content)
    fe.link(href=f"{host_url}/alerts/" + alert_url)
    fe.summary(alert.content[:40] + "...")
    fe.published(alert.approved_at)
