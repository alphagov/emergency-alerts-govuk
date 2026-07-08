// The "stopped sending" datetime attributes are emitted by the server as
// "YYYY-MM-DD HH:MM ZZZ", where ZZZ is a Europe/London timezone abbreviation
// (GMT in winter, BST in summer). Browsers' legacy Date parser understands the
// "GMT" abbreviation but NOT "BST", so `new Date('2025-06-26 09:27 BST')`
// returns an Invalid Date. That surfaced as "Stopped sending at invalid (DATE)
// on Invalid Date" once the clocks went forward. Map the London abbreviation to
// a numeric UTC offset so parsing is reliable all year round. ISO 8601 strings
// (e.g. the feed's published date) are passed straight through.
function parseFeedDatetime (datetimeString) {
  const londonOffsets = { GMT: '+00:00', UTC: '+00:00', BST: '+01:00' }
  const match = datetimeString.match(/^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) ([A-Z]+)$/)

  if (match) {
    const [, date, time, abbreviation] = match
    const offset = londonOffsets[abbreviation]

    if (offset) {
      return new Date(`${date}T${time}:00${offset}`)
    }
  }

  return new Date(datetimeString)
}

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.local-time').forEach(function (element) {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
    const locale = Intl.DateTimeFormat().resolvedOptions().locale
    const datetimeString = element.getAttribute('data-datetime')
    const datetimeObj = parseFeedDatetime(datetimeString)

    const localDate = datetimeObj.toLocaleString(locale, {
      timezone: tz,
      timeZoneName: 'short'
    })

    // convert from 'DD/MM/YYYY, HH:MM:SS TZ' to 'YYYY-MM-DD HH:MM TZ'
    const displayDate = localDate.replace(
      /(\d{2})\/(\d{2})\/(\d{4}), (\d{2}:\d{2}):\d{2} (\w+)/,
      '$3-$2-$1 $4 $5'
    )

    element.textContent = displayDate
  })

  document.querySelectorAll('.local-end-time').forEach(function (element) {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
    const locale = Intl.DateTimeFormat().resolvedOptions().locale
    const datetimeString = element.getAttribute('data-datetime')

    const datetimeObj = parseFeedDatetime(datetimeString)

    const fullTimeStr = datetimeObj
      .toLocaleTimeString(locale, {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
        timeZone: tz,
        timeZoneName: 'short'
      })
      .toLowerCase()

    // Split to separate time and timezone
    const parts = fullTimeStr.split(' ')
    const time = parts.slice(0, -1).join('').replace(' ', '') // "1:33pm"
    const timezone = parts[parts.length - 1].toUpperCase() // "GMT"

    const timeStr = `${time} (${timezone})`

    // Format the date (e.g., "Monday 24 November 2025")
    const dateStr = datetimeObj.toLocaleDateString(locale, {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: tz
    })

    element.textContent = `${timeStr} on ${dateStr}`
  })
})
