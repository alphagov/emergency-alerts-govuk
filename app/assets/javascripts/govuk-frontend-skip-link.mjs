import { SkipLink } from 'govuk-frontend'

export default function govukFrontendSkipLink () {
  var skipLinks = document.querySelectorAll('[data-module="govuk-skip-link"]')
  var i;

  for (i = 0; i < skipLinks.length; i++) {
    new SkipLink(skipLinks[i]).init()
  }
}
