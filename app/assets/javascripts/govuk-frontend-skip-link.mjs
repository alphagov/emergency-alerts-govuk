import { nodeListForEach } from 'govuk-frontend/govuk/common'
import SkipLink from 'govuk-frontend/govuk/components/skip-link/skip-link'

export default function govukFrontendSkipLink () {
  var skipLinks = document.querySelectorAll('[data-module="govuk-skip-link"]')

  nodeListForEach(skipLinks, function (skipLink) {
    new SkipLink(skipLink).init()
  })
}
