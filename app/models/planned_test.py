from emergency_alerts_utils.serialised_model import SerialisedModel

from app.models.alert_date import AlertDate


class PlannedTest(SerialisedModel):
    ALLOWED_PROPERTIES = {
        'description',
        'display_areas',
        'starts_at',
    }

    def __lt__(self, other):
        return self.starts_at < other.starts_at

    @property
    def starts_at_date(self):
        return AlertDate(self.starts_at)
