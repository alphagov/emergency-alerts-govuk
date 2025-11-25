document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".local-time").forEach(function (element) {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const locale = Intl.DateTimeFormat().resolvedOptions().locale;
    const datetimeString = element.getAttribute("data-datetime");
    const datetimeObj = new Date(datetimeString);

    const localDate = datetimeObj.toLocaleString(locale, {
      timezone: tz,
      timeZoneName: "short",
    });

    // convert from 'DD/MM/YYYY, HH:MM:SS TZ' to 'YYYY-MM-DD HH:MM TZ'
    const displayDate = localDate.replace(
      /(\d{2})\/(\d{2})\/(\d{4}), (\d{2}:\d{2}):\d{2} (\w+)/,
      "$3-$2-$1 $4 $5"
    );

    element.textContent = displayDate;
  });

  document.querySelectorAll(".local-end-time").forEach(function (element) {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const locale = Intl.DateTimeFormat().resolvedOptions().locale;
    const datetimeString = element.getAttribute("data-datetime");

    console.log("datetimeString: ", datetimeString);

    const datetimeObj = new Date(datetimeString);

    const fullTimeStr = datetimeObj
      .toLocaleTimeString(locale, {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
        timeZone: tz,
        timeZoneName: "short",
      })
      .toLowerCase();

    console.log("fullTimeStr:", fullTimeStr);

    // Split to separate time and timezone
    const parts = fullTimeStr.split(" ");
    const time = parts.slice(0, -1).join("").replace(" ", ""); // "1:33pm"
    const timezone = parts[parts.length - 1].toUpperCase(); // "GMT"

    const timeStr = `${time} (${timezone})`;

    // Format the date (e.g., "Monday 24 November 2025")
    const dateStr = datetimeObj.toLocaleDateString(locale, {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: tz,
    });

    console.log("dateStr: ", dateStr);

    element.textContent = `${timeStr} on ${dateStr}`;
  });
});
