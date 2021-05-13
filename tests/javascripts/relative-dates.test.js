import relativeDates from '../../src/assets/javascripts/relative-dates.mjs'

afterEach(() => {
  document.body.innerHTML = ''
})

test('It can handle a page with no datetimes in', () => {
  let error = false

  // import module for side effects
  try {
    relativeDates()
  } catch (e) {
    error = true
  }

  expect(error).toBe(false)

})

describe('If there are datetimes in the page', () => {

  beforeEach(() => {
    document.body.innerHTML = '<time class="relative-date" datetime="2021-04-07T15:04:51+00:00">7 April 2021 at 15:04</time>'
  })

  test('If there is no prefix, it still converts the datetime', () => {
    document.body.innerHTML = '<span class="relative-date__prefix">on </span>' + document.body.innerHTML

    relativeDates()

    expect(document.body.querySelector('.relative-date').hasAttribute('timeago-id')).toBe(true)
  })

  test('If there is a prefix, it removes it before converting the datetime', () => {
    document.body.innerHTML = `<span class="relative-date__prefix">on </span>` + document.body.innerHTML

    relativeDates()

    expect(document.body.querySelector('.relative-date__prefix')).toBeNull()
    expect(document.body.querySelector('.relative-date').hasAttribute('timeago-id')).toBe(true)
  })

})
