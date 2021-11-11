from collections import defaultdict

import yaml
from notifications_utils.serialised_model import SerialisedModelCollection

from app import alerts_api_client
from app.models.alert import Alert
from app.models.alert_date import AlertDate
from app.models.planned_tests import PlannedTests
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
    def test_alerts_today(self):
        for alert in self:
            if alert.starts_at_date.is_today and not alert.is_public:
                # Only show at most one test alert for a given day
                return [alert]
        return []

    @property
    def planned_tests(self):
        return PlannedTests.from_yaml()

    @property
    def current_and_planned_test_alerts(self):
        return self.test_alerts_today + self.planned_tests

    @property
    def dates_of_current_and_planned_test_alerts(self):
        return {
            alert.starts_at_date.at_midday
            for alert in self.current_and_planned_test_alerts
        }

    @property
    def last_updated(self):
        return max(alert.starts_at for alert in self.current_and_public)

    @property
    def last_updated_date(self):
        return AlertDate(self.last_updated)

    @classmethod
    def load(cls):
        data = cls.from_yaml() + cls.from_api()
        return cls([
            alert_dict for alert_dict in data
            if 'simple_polygons' not in alert_dict['areas'] or
            is_in_uk(alert_dict['areas']['simple_polygons'])
        ])

    @classmethod
    def from_api(cls):
        return alerts_api_client.get_alerts()

    @classmethod
    def from_yaml(cls, path=REPO / 'data.yaml'):
        with path.open() as stream:
            return yaml.load(stream, Loader=yaml.CLoader)['alerts']
