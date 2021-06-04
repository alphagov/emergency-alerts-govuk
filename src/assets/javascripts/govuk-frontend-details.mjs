// JS Module used to combine all the JS modules used in the application into a single entry point,
//
// When processed by a bundler, this is turned into a Immediately Invoked Function Expression (IIFE)
// The IIFE format allows it to run in browsers that don't support JS Modules.
//
// Exported items will be added to the window.GOVUK namespace.
// For example, `export { initAll }` will assign `initAll` to `window.GOVUK.initAll`
import { nodeListForEach } from 'govuk-frontend/govuk/common'
import Details from 'govuk-frontend/govuk/components/details/details'

function initAll (options) {
  // Set the options to an empty object by default if no options are passed.
  options = typeof options !== 'undefined' ? options : {}

  // Allow the user to initialise GOV.UK Frontend in only certain sections of the page
  // Defaults to the entire document if nothing is set.
  var scope = typeof options.scope !== 'undefined' ? options.scope : document

  var $details = scope.querySelectorAll('[data-module="govuk-details"]')
  nodeListForEach($details, function ($detail) {
    new Details($detail).init()
  })
}

initAll()

export {
  initAll,
  Details
}
