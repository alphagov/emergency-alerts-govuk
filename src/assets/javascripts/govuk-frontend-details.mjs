import Details from 'govuk-frontend/govuk/components/details/details'

export default function govukFrontendDetails () {
  var details = document.querySelectorAll('[data-module="govuk-details"]')
  var detailsLen = details.length
  var idx

  for (idx = 0; idx < detailsLen; idx++) {
    new Details(details[idx]).init()
  }
}
