import Button from 'govuk-frontend/govuk/components/button/button'

export default function sharingButton () {
  var container = document.querySelector('.share-url')
  var btn = document.createElement('button')
  var url = container.querySelector('.govuk-body')
  var urlString
  var onClick

  // return early if no of the required APIs are available
  if (!navigator.share && !document.queryCommandSupported('copy')) return

  btn.className = 'govuk-button govuk-button--secondary'
  btn.setAttribute('data-module', 'govuk-button')
  if (navigator.share) {
    btn.innerHTML = 'Share link'
  } else if (document.queryCommandSupported('copy')) {
    btn.innerHTML = 'Copy link'
  }

  if (navigator.share) {
    // Regexp taken from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/trim#polyfill
    urlString = url.innerHTML.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '')

    onClick = function (evt) {
      try {
        navigator.share({
          text: urlString.replace('https://', ''),
          url: urlString
        })
      } catch (e) {} // implement error handling if we surface this in the interface
    }
  } else {
    onClick = function (evt) {
      var selection = window.getSelection ? window.getSelection() : document.selection
      var range = document.createRange()

      selection.removeAllRanges()
      range.selectNodeContents(url)
      selection.addRange(range)
      document.execCommand('copy')
      selection.removeAllRanges()
    }
  }

  btn.addEventListener('click', onClick, false)
  new Button(btn).init()
  container.appendChild(btn)
}
