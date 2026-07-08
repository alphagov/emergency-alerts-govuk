// The feed's client-side date rendering must work in both GMT (winter) and BST
// (summer). Historically `new Date('... BST')` returned an Invalid Date, which
// rendered as "invalid (DATE) on Invalid Date". Pin the timezone so the parsed
// instant is deterministic regardless of where the tests run. The exact
// human-readable formatting (e.g. "BST" vs "GMT+1", comma placement) depends on
// the runtime's locale/ICU data, so these tests assert the meaningful parts
// rather than an exact string.
process.env.TZ = 'Europe/London'

import '../../app/assets/javascripts/feed.js'

const render = () => {
  document.dispatchEvent(new Event('DOMContentLoaded'))
}

afterEach(() => {
  document.body.innerHTML = ''
})

describe('The "Stopped sending at" time (.local-end-time)', () => {
  test('renders a BST (summer) datetime instead of "Invalid Date"', () => {
    document.body.innerHTML =
      '<time class="local-end-time" data-datetime="2025-06-26 09:27 BST"></time>'

    render()

    const text = document.querySelector('.local-end-time').textContent
    expect(text).not.toMatch(/invalid/i)
    expect(text).toContain('9:27am')
    expect(text).toMatch(/June/)
    expect(text).toMatch(/26/)
    expect(text).toMatch(/2025/)
  })

  test('renders a GMT (winter) datetime instead of "Invalid Date"', () => {
    document.body.innerHTML =
      '<time class="local-end-time" data-datetime="2025-11-26 09:27 GMT"></time>'

    render()

    const text = document.querySelector('.local-end-time').textContent
    expect(text).not.toMatch(/invalid/i)
    expect(text).toContain('9:27am')
    expect(text).toMatch(/November/)
    expect(text).toMatch(/26/)
    expect(text).toMatch(/2025/)
  })
})

describe('The "Published" time (.local-time)', () => {
  test('parses an ISO 8601 published datetime (BST) without error', () => {
    document.body.innerHTML =
      '<time class="local-time" data-datetime="2025-06-26T09:27:00+01:00"></time>'

    render()

    const text = document.querySelector('.local-time').textContent
    expect(text).not.toMatch(/invalid/i)
    expect(text).toMatch(/2025/)
  })
})
