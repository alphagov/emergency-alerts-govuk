from bs4 import BeautifulSoup

from tests.src import env


def test_index_page():
    template = env.get_template("src/index.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert html.select_one('h1').text.strip() == "Emergency Alerts"
