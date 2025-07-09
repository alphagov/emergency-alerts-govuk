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
from lxml import etree as ET

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


def namespace(**kwargs):
    """Creates namespace, to be added as a jinja environment global to avoid `'namespace' is undefined"`
    error when using govuk-frontend-jinja templates, as they use namespace to store attributes.
    """
    class Namespace:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    return Namespace(**kwargs)


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
        "namespace": namespace
    }

    return env


def get_rendered_pages(alerts):
    env = setup_jinja_environment(alerts)
    rendered = {}

    fg = _get_feed_generator("EN")
    fg_cy = _get_feed_generator("CY")
    feed_item_count = 0

    for path in all_view_paths:
        template = env.get_template(path)
        target = path.replace(".html", "")

        if target.endswith('.cy'):
            notification_banner_text = "Byddwn yn profi system Rhybuddion Argyfwng y DU ar ddydd Sul 7 Medi am 3yh."
        else:
            notification_banner_text = "We are testing the UK’s Emergency Alerts system on Sunday 7 September at 3pm."

        # render each individual alert's page
        if target == 'alert':
            for alert in alerts.public:
                alert_url = get_url_for_alert(alert, alerts)
                rendered["alerts/" + alert_url] = template.render({
                    'alert_data': alert, 'notification_banner_text': notification_banner_text})
                if feed_item_count < 20:
                    _add_feed_entry(fg, alert, alert_url)
                    _add_feed_entry(fg_cy, alert, alert_url)
                    feed_item_count += 1
            continue

        # Render each alert's page in Welsh
        if target == 'alert.cy':
            for alert in alerts.public:
                alert_url = get_url_for_alert(alert, alerts)
                rendered["alerts/" + alert_url + ".cy"] = template.render({
                    'alert_data': alert,
                    'notification_banner_text': notification_banner_text})
            continue

        if target == 'index':
            rendered['alerts'] = template.render(notification_banner_text=notification_banner_text)
            continue

        if target == 'index.cy':
            rendered['alerts/about.cy'] = template.render(notification_banner_text=notification_banner_text)
            continue

        rendered["alerts/" + target] = template.render(notification_banner_text=notification_banner_text)

    rendered['alerts/feed.atom'] = _add_stylesheet_attribute_to_atom(
        fg.atom_str(pretty=True).decode("utf-8")
    )
    with open(REPO / 'app/assets/stylesheets/feed.xsl', "r", encoding="utf-8") as file:
        xsl_content = file.read()
        xsl_content = _add_stylesheet_link_to_xsl(xsl_content)
        rendered['alerts/feed.xsl'] = xsl_content

    rendered['alerts/feed_cy.atom'] = _add_stylesheet_attribute_to_atom(
        fg_cy.atom_str(pretty=True).decode("utf-8"),
        style_path="feed_cy.xsl"
    )
    with open(REPO / 'app/assets/stylesheets/feed_cy.xsl', "r", encoding="utf-8") as file:
        xsl_content = file.read()
        xsl_content = _add_stylesheet_link_to_xsl(xsl_content)
        rendered['alerts/feed_cy.xsl'] = xsl_content

    return rendered


def _get_feed_generator(lang="EN"):

    host_url = current_app.config["GOVUK_ALERTS_HOST_URL"]

    fg = FeedGenerator()

    if lang == "EN":
        fg.id(f"{host_url}/alerts/feed.atom")
        fg.title("Emergency Alerts")
        fg.author(name="Emergency Alerts Service", uri="https://www.gov.uk/contact/govuk")
        fg.generator("gov.uk")
        fg.link(
            href=f"{host_url}/alerts/feed.atom",
            type="application/atom+xml",
            rel="self",
        )
        fg.link(
            href=f"{host_url}/alerts",
            type="application/html",
            rel="via",
        )
        fg.link(
            href=f"{host_url}/alerts",
            type="application/html",
            rel="alternate",
        )
        fg.icon(icon=file_fingerprint("/alerts/assets/images/favicon.ico"))
        fg.logo(logo=file_fingerprint("/alerts/assets/images/govuk-opengraph-image.png"))
        fg.subtitle("GOV.UK Emergency Alerts")
        fg.language("en-US")
        fg.rights(
            "Released under the Open Government Licence (OGL), "
            "citation of publisher and online resource required on reuse."
        )
    elif lang == "CY":
        fg.id(f"{host_url}/alerts/feed.atom.cy")
        fg.title("Emergency Alerts")
        fg.author(name="Gwasanaeth Rhybuddion Argyfwng", uri="https://www.gov.uk/contact/govuk")
        fg.generator("gov.uk")
        fg.link(
            href=f"{host_url}/alerts/feed.atom.cy",
            type="application/atom+xml",
            rel="self",
        )
        fg.link(
            href=f"{host_url}/alerts/about.cy",
            type="application/html",
            rel="via",
        )
        fg.link(
            href=f"{host_url}/alerts/about.cy",
            type="application/html",
            rel="alternate",
        )
        fg.icon(icon=file_fingerprint("/alerts/assets/images/favicon.ico"))
        fg.logo(logo=file_fingerprint("/alerts/assets/images/govuk-opengraph-image.png"))
        fg.subtitle("Rybuddion Argyfwng GOV.UK")
        fg.language("en-US")
        fg.rights(
            "Rhyddhawyd o dan y Drwydded Llywodraeth Agored (OGL), "
            "dyfynnu cyhoeddwr ac adnodd ar-lein sydd ei angen ar ailddefnyddio."
        )

    return fg


def _add_feed_entry(fg, alert, alert_url):

    host_url = current_app.config["GOVUK_ALERTS_HOST_URL"]

    title = alert_url
    if alert.areas.get("aggregate_names"):
        title = ", ".join(alert.areas["aggregate_names"])
    else:
        title = ", ".join(alert.areas["names"])

    fe = fg.add_entry()
    fe.id(f"{host_url}/alerts/" + alert_url)
    fe.title(title)
    fe.updated(alert.approved_at)
    fe.author(name="Emergency Alerts Service", uri="https://www.gov.uk/contact/govuk")
    fe.content(alert.content)
    fe.link(href=f"{host_url}/alerts/" + alert_url, rel="alternate")
    content = alert.content if len(alert.content) <= 40 else alert.content[:36] + "..."
    fe.summary(content)
    if alert.extra_content:
        fe.subtitle(alert.extra_content)
    fe.published(alert.approved_at)


def _add_stylesheet_attribute_to_atom(feed_string, style_path="feed.xsl"):
    feed = ET.fromstring(feed_string.encode("utf-8"))
    return ET.tostring(
        feed,
        doctype=f'<?xml-stylesheet href="{style_path}" type="text/xsl"?>',
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True
    ).decode("utf-8")


def _add_stylesheet_link_to_xsl(xsl_content):
    stylesheet_href = file_fingerprint("/alerts/assets/stylesheets/main.css")
    new_content = xsl_content.replace("main.css", stylesheet_href)
    return new_content
