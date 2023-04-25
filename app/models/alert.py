from datetime import datetime, timedelta

import pytz
from emergency_alerts_utils.serialised_model import SerialisedModel

from app.models.alert_date import AlertDate


class Alert(SerialisedModel):
    ALLOWED_PROPERTIES = {
        'id',
        'channel',
        'approved_at',
        'starts_at',
        'cancelled_at',
        'finishes_at',
        'areas',
        'content',
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
    def starts_at_date(self):
        return AlertDate(self.starts_at)

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
    def is_planned(self):
        now = datetime.now(pytz.utc)
        return self.expires_date.as_utc_datetime >= now

    @property
    def is_current(self):
        now = datetime.now(pytz.utc)

        return (
            self.expires_date.as_utc_datetime >= now and
            self.approved_at_date.as_utc_datetime <= now
        )

    @property
    def is_expired(self):
        now = datetime.now(pytz.utc)
        return self.expires_date.as_utc_datetime < now

    @property
    def is_past(self):
        if self.is_public:
            return self.is_expired
        # Only show service tests for a limited time in past
        else:
            return self.is_expired and not self.starts_at_date.is_today and \
                not self.is_active_test and not self.is_archived_test

    @property
    def is_active_test(self):
        # An alert is considered active if it started in the last hour.
        now = datetime.now(pytz.utc)
        return self.expires_date.as_utc_datetime >= now \
            and self.starts_at_date.as_utc_datetime <= now \
            and not self.is_public

    @property
    def is_archived_test(self):
        # An alert is considered archived (and therefore shouldn't be shown)
        # if it's a test that ended over 48 hours ago
        archival_point = (datetime.now(pytz.utc) - timedelta(hours=48))
        return self.expires_date.as_utc_datetime <= archival_point \
            and not self.is_public
