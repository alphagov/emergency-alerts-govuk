import { nodeListForEach } from 'govuk-frontend/govuk/common.js'
import Details from 'govuk-frontend/govuk/components/details/details.js'

export default function govukFrontendDetails () {
  var details = document.querySelectorAll('[data-module="govuk-details"]')

  nodeListForEach(details, function (detail) {
    new Details(detail).init()
  })
}
