class AlertsDate(object):
    """Makes a datetime available in different formats"""

    def __init__(self, _datetime):
        self._datetime = _datetime

    @property
    def as_lang(self, lang='en-GB'):
        return '{dt.day} {dt:%B} {dt:%Y} at {dt:%H}:{dt:%M}'.format(dt=self._datetime)

    @property
    def as_iso8601(self):
        return self._datetime.isoformat()

    @property
    def as_datetime(self):
        return self._datetime
