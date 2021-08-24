from app.render import VIEWS


def test_all_pages_with_details_in_have_the_js_for_it():
    detailsImport = 'from "govuk_frontend_jinja/components/details/macro.html" import govukDetails'

    for path in VIEWS.glob('*.html'):
        with open(path) as template:
            template_str = template.read()
            if detailsImport in template_str:
                assert '/alerts/assets/javascripts/govuk-frontend-details' in template_str
