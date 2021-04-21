import { render } from 'timeago.js'

function relativeDates () {
  var nodes = document.querySelectorAll('.relative-date')
  var nodesLength = nodes.length
  var i
  var parentNode
  var prefix

  render(nodes)

  for (i = 0; i < nodesLength; i++) {
    parentNode = nodes[i].parentNode
    prefix = parentNode.querySelector('.relative-date__prefix')
    if (prefix) {
      parentNode.removeChild(prefix)
    }
  }
}

relativeDates()
