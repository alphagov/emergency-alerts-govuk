from collections import defaultdict

import yaml
from notifications_utils.serialised_model import SerialisedModelCollection

from app.models.alert import Alert
from app.models.alert_date import AlertDate
from app.utils import REPO, is_in_uk


class Alerts(SerialisedModelCollection):
    model = Alert

    @property
    def current_and_public(self):
        return [alert for alert in self if alert.is_current_and_public]

    @property
    def expired(self):
        return [alert for alert in self if alert.is_expired]

    @property
    def expired_grouped_by_date(self):
        alerts_by_date = defaultdict(list)
        for alert in self.expired:
            if alert.is_public or all(
                already_grouped_alert.is_public
                for already_grouped_alert in alerts_by_date[alert.starts_at_date.as_local_date]
            ):
                alerts_by_date[alert.starts_at_date.as_local_date].append(alert)
        return alerts_by_date.items()

    @property
    def public(self):
        return [alert for alert in self if alert.is_public]

    @property
    def last_updated(self):
        return max(alert.starts_at for alert in self.current_and_public)

    @property
    def last_updated_date(self):
        return AlertDate(self.last_updated)

    # We'll have multiple datasources in future. Having this
    # method now gives a clean abstraction so we don't have to
    # change too much when we add them (and remove this comment!)
    @classmethod
    def load(cls):
        return cls.from_yaml()

    @classmethod
    def from_yaml(cls, path=REPO / 'data.yaml'):
        with path.open() as stream:
            data = yaml.load(stream, Loader=yaml.CLoader)

        return cls([
            alert_dict for alert_dict in data['alerts']
            if 'simple_polygons' not in alert_dict['areas'] or
            is_in_uk(alert_dict['areas']['simple_polygons'])
        ])
