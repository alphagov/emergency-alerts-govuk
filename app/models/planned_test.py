from emergency_alerts_utils.serialised_model import SerialisedModel

from app.models.alert_date import AlertDate


class PlannedTest(SerialisedModel):
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
        return self.starts_at < other.starts_at

    @property
    def starts_at_date(self):
        return AlertDate(self.starts_at)
