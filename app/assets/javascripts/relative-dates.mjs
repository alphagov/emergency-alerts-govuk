import { render } from 'timeago.js'

export default function relativeDates () {
  const nodes = document.querySelectorAll('.relative-date')
  const nodesLength = nodes.length
  let i
  let parentNode
  let prefix

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
