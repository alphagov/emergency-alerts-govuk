from datetime import datetime

import pytz
from notifications_utils.serialised_model import SerialisedModel

from app.models.alert_date import AlertDate


class BaseAlert(SerialisedModel):
    ALLOWED_PROPERTIES = {
        'starts_at',
        'content',
    }

    @property
    def starts_at_date(self):
        return AlertDate(self.starts_at)


class Alert(BaseAlert):
    ALLOWED_PROPERTIES = BaseAlert.ALLOWED_PROPERTIES | {
        'id',
        'channel',
        'approved_at',
        'cancelled_at',
        'finishes_at',
        'areas',
    }

    def __lt__(self, other):
        return (self.starts_at, self.id) < (other.starts_at, other.id)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def display_areas(self):
        if "aggregate_names" in self.areas:
            return self.areas["aggregate_names"]

        return self.areas.get("names", [])

    @property
    def approved_at_date(self):
        return AlertDate(self.approved_at)

    @property
    def expires_date(self):
        return self.cancelled_at_date or self.finishes_at_date

    @property
    def finishes_at_date(self):
        return AlertDate(self.finishes_at)

    @property
    def cancelled_at_date(self):
        if self.cancelled_at:
            return AlertDate(self.cancelled_at)

    @property
    def is_current_and_public(self):
        return self.is_current and self.is_public

    @property
    def is_public(self):
        return self.channel in ['government', 'severe']

    @property
    def is_expired(self):
        now = datetime.now(pytz.utc)
        return self.expires_date.as_utc_datetime < now

    @property
    def is_current(self):
        now = datetime.now(pytz.utc)

        return (
            self.expires_date.as_utc_datetime >= now and
            self.approved_at_date.as_utc_datetime <= now
        )


class PlannedTest(BaseAlert):
    ALLOWED_PROPERTIES = BaseAlert.ALLOWED_PROPERTIES | {
        'display_areas',
    }

    def __lt__(self, other):
        return self.starts_at < other.starts_at
