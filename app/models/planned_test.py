from datetime import datetime

import pytz
from emergency_alerts_utils.serialised_model import SerialisedModel

from app.models.alert_date import AlertDate


class PlannedTest(SerialisedModel):
    ALLOWED_PROPERTIES = {
        'id',
        'channel',
        'approved_at',
        'starts_at',
        'starts_at_datetime_in_welsh',
        'cancelled_at',
        'finishes_at',
        'areas',
        'areas_in_welsh',
        'display_in_status_box',
        'status_box_content',
        'welsh_status_box_content',
        'summary',
        'welsh_summary',
        'content',
        'welsh_content',
        'display_as_link',
        'extra_content',
        'planned_tests_link'
    }

    def __lt__(self, other):
        return self.starts_at < other.starts_at

    @property
    def display_areas(self):

        if "aggregate_names" in self.areas:
            return self.areas["aggregate_names"]

        return self.areas.get("names", [])

    @property
    def display_areas_in_welsh(self):

        if not self.areas_in_welsh:
            return None
        if "aggregate_names" in self.areas_in_welsh:
            return self.areas_in_welsh["aggregate_names"]

        return self.areas_in_welsh.get("names", [])

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
    def is_public(self):
        return self.channel in ["government", "severe"]

    @property
    def is_planned(self):
        now = datetime.now(pytz.utc)
        return self.expires_date.as_utc_datetime >= now

    @property
    def planned_tests_page(self):
        return self.planned_tests_link or "announcements"
