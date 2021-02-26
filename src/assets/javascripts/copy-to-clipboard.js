var container = document.querySelector('.share-url'),
    btn = document.createElement('button'),
    url = container.querySelector('.govuk-body');

btn.className = 'govuk-button govuk-button--secondary';
btn.setAttribute('data-module', 'govuk-button');
btn.innerHTML = '<span class="govuk-visually-hidden">Copy </span>' +
                'Share link' +
                '<span class="govuk-visually-hidden"> to clipboard</span>';

btn.addEventListener('click', function (evt) {
  var selection = window.getSelection ? window.getSelection() : document.selection,
      range = document.createRange();

  selection.removeAllRanges();
  range.selectNodeContents(url);
  selection.addRange(range);
  document.execCommand('copy');
  selection.removeAllRanges();
}, false);

container.appendChild(btn);
