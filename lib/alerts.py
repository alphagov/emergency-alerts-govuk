import yaml
from notifications_utils.serialised_model import SerialisedModelCollection

from lib.alert import Alert
from lib.alert_date import AlertDate
from lib.utils import is_in_uk


class Alerts(SerialisedModelCollection):
    model = Alert

    @property
    def current_and_public(self):
        return [alert for alert in self if alert.is_current_and_public]

    @property
    def expired(self):
        return [alert for alert in self if alert.is_expired]

    @property
    def public(self):
        return [alert for alert in self if alert.is_public]

    @property
    def last_updated(self):
        return max(alert.starts_at for alert in self.current_and_public)

    @property
    def last_updated_date(self):
        return AlertDate(self.last_updated)

    @classmethod
    def from_yaml(cls, path):
        with path.open() as stream:
            data = yaml.load(stream, Loader=yaml.CLoader)

        return cls([
            alert_dict for alert_dict in data['alerts']
            if 'simple_polygons' not in alert_dict['areas'] or
            is_in_uk(alert_dict['areas']['simple_polygons'])
        ])
