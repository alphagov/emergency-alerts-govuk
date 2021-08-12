from app.render import alerts_from_yaml, get_rendered_pages


def write_to_disk():
    alerts = alerts_from_yaml()
    rendered_pages = get_rendered_pages(alerts)

    for filename, content in rendered_pages.items():
        target = filename
        if filename == "alerts":
            target = "index.html"

        with open(f"dist/{target}", "w") as fp:
            fp.write(content)


if __name__ == "__main__":
    write_to_disk()
