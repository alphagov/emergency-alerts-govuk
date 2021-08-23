from glob import glob


def test_all_pages_with_details_in_have_the_js_for_it():
    detailsImport = 'from "govuk_frontend_jinja/components/details/macro.html" import govukDetails'

    for template_path in glob('./src/*.html'):
        with open(template_path) as template:
            template_str = template.read()
            if detailsImport in template_str:
                assert '/alerts/assets/javascripts/govuk-frontend-details' in template_str
