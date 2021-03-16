var container = document.querySelector('.share-url'),
    btn = document.createElement('button'),
    url = container.querySelector('.govuk-body'),
    urlString,
    onClick;

btn.className = 'govuk-button govuk-button--secondary';
btn.setAttribute('data-module', 'govuk-button');
if (navigator.share) {
  btn.innerHTML = 'Share link';
} else {
  btn.innerHTML = 'Copy link';
}

if (navigator.share) {

  urlString = url.innerHTML.replace(/^[\s]+$/, '');

  onClick = function (evt) {
    try {
      navigator.share({
        "text": urlString.replace('https://', ''),
        "url": urlString
      });
    } catch (e) {} // implement error handling if we surface this in the interface
  };

} else {

  onClick = function (evt) {
    var selection = window.getSelection ? window.getSelection() : document.selection,
        range = document.createRange();

    selection.removeAllRanges();
    range.selectNodeContents(url);
    selection.addRange(range);
    document.execCommand('copy');
    selection.removeAllRanges();
  };
}

btn.addEventListener('click', onClick, false);
container.appendChild(btn);
