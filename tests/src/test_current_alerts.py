from bs4 import BeautifulSoup

from tests.src import env


def test_current_alerts_page():
    template = env.get_template("src/current-alerts.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert html.select_one('h1').text.strip() == "Current alerts"
