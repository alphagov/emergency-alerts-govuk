import yaml
from notifications_utils.serialised_model import SerialisedModelCollection

from lib.alert import Alert
from lib.alert_date import AlertDate


class Alerts(SerialisedModelCollection):
    model = Alert

    @property
    def current_and_public(self):
        return [alert for alert in self if alert.is_current_and_public]

    @property
    def expired_or_test(self):
        return [alert for alert in self if alert.is_expired_or_test]

    @property
    def last_updated(self):
        return max(alert.starts for alert in self.current_and_public)

    @property
    def last_updated_date(self):
        return AlertDate(self.last_updated)

    @classmethod
    def from_yaml(cls, path):
        with path.open() as stream:
            data = yaml.load(stream, Loader=yaml.CLoader)

        return cls(data['alerts'])

    def by_message_type(self, message_type):
        return [
            alert for alert in self if alert.message_type == message_type
        ]
