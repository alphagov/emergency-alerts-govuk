import { Details } from 'govuk-frontend'

export default function govukFrontendDetails () {
  var details = document.querySelectorAll('[data-module="govuk-details"]')
  var i;

  for (i = 0; i < details.length; i++) {
    new Details(details[i]).init()
  }
}
