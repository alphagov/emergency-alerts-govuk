from tests.conftest import render_template


def test_index_page(env):
    html = render_template(env, "src/index.html")
    assert html.select_one('h1').text.strip() == "Emergency Alerts"
