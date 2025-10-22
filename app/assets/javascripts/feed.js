document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.local-time').forEach(function (element) {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
    const locale = Intl.DateTimeFormat().resolvedOptions().locale
    const datetimeString = element.getAttribute('data-datetime')
    const datetimeObj = new Date(datetimeString)
    const localDate = datetimeObj.toLocaleString(locale, {
      timezone: tz,
      timeZoneName: 'short',
    })
    // convert from 'DD/MM/YYYY, HH:MM:SS TZ' to 'YYYY-MM-DD HH:MM TZ'
    const displayDate = localDate.replace(
      /(\d{2})\/(\d{2})\/(\d{4}), (\d{2}:\d{2}):\d{2} (\w+)/,
      '$3-$2-$1 $4 $5'
    )
    element.textContent = displayDate
  })
})
