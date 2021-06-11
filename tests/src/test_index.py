from bs4 import BeautifulSoup


def test_index_page(env):
    template = env.get_template("src/index.html")
    content = template.render()
    html = BeautifulSoup(content, 'html.parser')
    assert html.select_one('h1').text.strip() == "Emergency Alerts"
