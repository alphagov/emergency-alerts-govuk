import { nodeListForEach } from 'govuk-frontend/govuk/common.js'
import SkipLink from 'govuk-frontend/govuk/components/skip-link/skip-link.js'

export default function govukFrontendSkipLink () {
  var skipLinks = document.querySelectorAll('[data-module="govuk-skip-link"]')

  nodeListForEach(skipLinks, function (skipLink) {
    new SkipLink(skipLink).init()
  })
}
