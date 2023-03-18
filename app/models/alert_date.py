import datetime

import pytz
from emergency_alerts_utils.timezones import (
    local_timezone,
    utc_string_to_aware_gmt_datetime,
)


class AlertDate(object):
    """Makes a datetime available in different formats"""

    def __init__(self, _datetime):
        self._datetime = _datetime  # a timezone-aware UTC datetime
        self._local_datetime = utc_string_to_aware_gmt_datetime(self._datetime)

    def __eq__(self, other):
        return self._datetime == other._datetime

    def __lt__(self, other):
        return self._datetime < other._datetime

    def __hash__(self):
        return hash(self._datetime)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._datetime})'

    @property
    def time_as_lang(self):
        return {
            '12:00AM': 'Midnight',
            '12:00PM': 'Midday'
        }.get(
            f'{self._local_datetime:%-I:%M%p}',
            f'{self._local_datetime:%-I:%M%p}',
        ).lower()

    @property
    def date_as_lang(self):
        dt = self._local_datetime
        return f'{dt:%A} {dt.day} {dt:%B} {dt:%Y}'

    @property
    def as_url(self):
        """
        * non-zero padded day
        * lower case month abbrevation
        * full year

        3-jun-2021
        """
        dt = self._local_datetime
        return f'{dt:%-d}-{dt:%b}-{dt:%Y}'.lower()

    @property
    def as_lang(self, lang='en-GB'):
        return f'at {self.time_as_lang} on {self.date_as_lang}'

    @property
    def as_alert_lang(self, lang='en-GB'):
        dt = self._local_datetime
        return f'{dt:%A} {dt.day} {dt:%B} {dt:%Y}, at {dt:%-I%p}'

    @property
    def as_alert_date_lang(self, lang='en-GB'):
        dt = self._local_datetime
        return f'{dt:%A} {dt.day} {dt:%B} {dt:%Y}'

    @property
    def as_iso8601(self):
        return self._local_datetime.isoformat()

    @property
    def as_iso8601_date(self):
        return self._local_datetime.date().isoformat()

    @property
    def as_utc_datetime(self):
        return self._datetime

    @property
    def as_local_datetime(self):
        return self._local_datetime

    @property
    def as_local_date(self):
        return self._local_datetime.date()

    @property
    def at_midday(self):
        return self.__class__(
            datetime.datetime.combine(
                self.as_local_date,
                datetime.time(hour=12, minute=0),
                tzinfo=local_timezone,
            ).astimezone(pytz.utc)
        )

    @classmethod
    def now(cls):
        return cls(datetime.datetime.utcnow())

    @property
    def is_today(self):
        return self.as_local_date == self.now().as_local_date
