export default function sharingButton () {
  var container = document.querySelector('.share-url')
  var btn = document.createElement('button')
  var url = container.querySelector('.govuk-body')
  var urlString
  var onClick

  btn.className = 'govuk-button govuk-button--secondary'
  btn.setAttribute('data-module', 'govuk-button')
  if (navigator.share) {
    btn.innerHTML = 'Share link'
  } else {
    btn.innerHTML = 'Copy link'
  }

  if (navigator.share) {
    urlString = url.innerHTML.replace(/^[\s]+$/, '')

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
  container.appendChild(btn)
}
