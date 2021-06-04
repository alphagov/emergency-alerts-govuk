import helpers from './support/helpers.js'
import sharingButton from '../../src/assets/javascripts/sharing-button.mjs'

const URL = 'https://www.gov.uk/alerts/3-may-2021'
const htmlFixture = `
      <div class="share-url">
        <p class="govuk-body">
          ${URL}
        </p>
      </div>`

afterAll(() => {
  // clear up methods in the global space
  document.queryCommandSupported = undefined
})

afterEach(() => {
  document.body.innerHTML = ''

  jest.restoreAllMocks()
})

describe('If the Web Share API is supported', () => {

  beforeEach(() => {

    navigator.share = jest.fn(() => {})

    // copy command would be supported if navigator.share is
    document.queryCommandSupported = jest.fn(command => command === 'copy')

    document.body.innerHTML = htmlFixture

    sharingButton()

  })

  afterEach(() => {

    delete navigator.share

  })

  describe('On page load', () => {

    test('A button should be added below the URL to be shared', () => {

      const URLParagraph = document.querySelector('.share-url > .govuk-body')

      expect(URLParagraph.nextElementSibling).not.toBe(null)
      expect(URLParagraph.nextElementSibling.classList.contains('govuk-button')).toBe(true)

    })

    test('The button should be for sharing the link', () => {

      const button = document.querySelector('.share-url > .govuk-button')

      expect(button.textContent.trim()).toEqual('Share link')

    })

  })

  describe('If the button is clicked', () => {

    test('The correct information should be sent to the Web Share API', () => {

      const button = document.querySelector('.share-url > .govuk-button')
      const clickEvent = new window.MouseEvent(
        'click',
        {
          view: window,
          bubbles: true,
          cancelable: true
        }
      )

      button.dispatchEvent(clickEvent)

      expect(navigator.share).toHaveBeenCalledWith({
        text: URL.replace(/^https:\/\//, ''),
        url: URL
      })

    })

  })

})

describe('If the Web Share API is not supported but the copy command is', () => {

  let selectionMock
  let rangeMock

  beforeEach(() => {

    // assume copy command is available
    document.queryCommandSupported = jest.fn(command => command === 'copy')

    // mock objects used to manipulate the page selection
    selectionMock = new helpers.SelectionMock(jest)
    rangeMock = new helpers.RangeMock(jest)

    // plug gaps in JSDOM's API for manipulation of selections
    window.getSelection = jest.fn(() => selectionMock)
    document.createRange = jest.fn(() => rangeMock)

    // plug JSDOM not having execCommand
    document.execCommand = jest.fn(() => {})

    document.body.innerHTML = htmlFixture
    sharingButton()

  })

  afterEach(() => {

    // reset mocked DOM APIs
    window.getSelection = undefined
    document.createRange = undefined
    document.execCommand = undefined

  })

  describe('On page load', () => {

    test('A button should be added below the URL to be shared', () => {

      const URLParagraph = document.querySelector('.share-url > .govuk-body')

      expect(URLParagraph.nextElementSibling).not.toBe(null)
      expect(URLParagraph.nextElementSibling.classList.contains('govuk-button')).toBe(true)

    })

    test('The button should be for copying the link', () => {

      const button = document.querySelector('.share-url > .govuk-button')

      expect(button.textContent.trim()).toEqual('Copy link')

    })

  })

  describe('If the button is clicked', () => {

    test('The correct information should be added to the clipboard', () => {

      const button = document.querySelector('.share-url > .govuk-button')
      const urlParagraph = document.querySelector('.share-url > .govuk-body')
      const clickEvent = new window.MouseEvent(
        'click',
        {
          view: window,
          bubbles: true,
          cancelable: true
        }
      )

      button.dispatchEvent(clickEvent)

      // it should make a selection (a range) from the paragraph containing the URL
      expect(rangeMock.selectNodeContents.mock.calls[0]).toEqual([urlParagraph])

      // that selection (a range) should be added to that for the page (a selection)
      expect(selectionMock.addRange.mock.calls[0]).toEqual([rangeMock])

      expect(document.execCommand).toHaveBeenCalled()
      expect(document.execCommand.mock.calls[0]).toEqual(['copy'])

    })

  })

})

describe('If neither the Web Share API or the copy command is supported', () => {

  test('On page load, the button should not be added', () => {

    document.body.innerHTML = htmlFixture

    // fake support for the copy command not being available
    document.queryCommandSupported = jest.fn(command => false)

    sharingButton()

    expect(document.querySelector('.share-url > .govuk-button')).toBe(null)

  })

})
