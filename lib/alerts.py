import yaml
from notifications_utils.serialised_model import SerialisedModelCollection

from lib.alert import Alert
from lib.alert_date import AlertDate


class Alerts(SerialisedModelCollection):
    model = Alert

    def __init__(self, data):
        self.last_updated = data['last_updated']
        super().__init__(data['alerts'])

    @property
    def current(self):
        return [alert for alert in self if alert.is_current]

    @property
    def last_updated_date(self):
        return AlertDate(self.last_updated)

    @classmethod
    def from_yaml(cls, path):
        with path.open() as stream:
            data = yaml.load(stream, Loader=yaml.CLoader)

        return cls(data)
