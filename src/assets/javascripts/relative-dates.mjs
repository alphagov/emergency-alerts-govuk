import { render } from 'timeago.js'

export default function relativeDates () {
  var nodes = document.querySelectorAll('.relative-date')
  var nodesLength = nodes.length
  var i
  var parentNode
  var prefix

  if (nodes.length === 0) return

  render(nodes)

  for (i = 0; i < nodesLength; i++) {
    parentNode = nodes[i].parentNode
    prefix = parentNode.querySelector('.relative-date__prefix')
    if (prefix) {
      parentNode.removeChild(prefix)
    }
  }
}
