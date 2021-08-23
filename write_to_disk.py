from app.models.alerts import Alerts
from app.render import get_rendered_pages

alerts = Alerts.load()
rendered_pages = get_rendered_pages(alerts)

for filename, content in rendered_pages.items():
    target = filename
    if filename == "alerts":
        target = "index.html"

    with open(f"dist/{target}", "w") as fp:
        fp.write(content)
