import pytz
from pytz import timezone


class AlertDate(object):
    """Makes a datetime available in different formats"""

    def __init__(self, _datetime):
        self._datetime = _datetime
        self._local_datetime = _datetime.astimezone(timezone('Europe/London'))

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
    def as_lang(self, lang='en-GB'):
        return f'at {self.time_as_lang} on {self.date_as_lang}'

    @property
    def as_iso8601(self):
        return self._local_datetime.isoformat()

    @property
    def as_utc_datetime(self):
        return self._datetime.astimezone(pytz.utc)

    @property
    def as_local_datetime(self):
        return self._local_datetime

    @property
    def as_local_date(self):
        return self._local_datetime.date()
