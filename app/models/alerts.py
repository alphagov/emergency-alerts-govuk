import time
from collections import defaultdict

import yaml
from emergency_alerts_utils.serialised_model import SerialisedModelCollection
from flask import current_app

from app import alerts_api_client
from app.models.alert import Alert
from app.models.alert_date import AlertDate
from app.models.planned_tests import PlannedTests
from app.utils import REPO, is_in_uk, put_timestamp_to_s3, setup_boto3_session


class Alerts(SerialisedModelCollection):
    model = Alert

    @property
    def public(self):
        return [alert for alert in self if alert.is_public]

    @property
    def current_and_public(self):
        return [alert for alert in self if alert.is_current_and_public]

    @property
    def non_public(self):
        return [
            alert for alert in self if alert.is_planned and not alert.is_public
            ]

    @property
    def test_alerts_today(self):
        return [
            alert for alert
            in self
            if alert.is_active_test and not alert.is_public
        ]

    @property
    def expired(self):
        return [alert for alert in self if alert.is_expired and not alert.is_archived_test]

    @property
    def past(self):
        return [alert for alert in self if alert.is_past]

    @property
    def last_updated(self):
        return max(alert.starts_at for alert in self.current_and_public)

    @property
    def last_updated_date(self):
        return AlertDate(self.last_updated)

    @property
    def test_alerts_today_grouped(self):
        alerts_by_date = defaultdict(list)
        for alert in self.test_alerts_today:
            alerts_by_date[alert.starts_at_date.as_local_date].append(alert)
        return alerts_by_date.items()

    @property
    def past_alerts_grouped_by_date(self):
        alerts_by_date = defaultdict(list)
        for alert in self.past:
            if alert.is_public or all(
                already_grouped_alert.is_public
                for already_grouped_alert in alerts_by_date[alert.starts_at_date.as_local_date]
            ):
                alerts_by_date[alert.starts_at_date.as_local_date].append(alert)
        return alerts_by_date.items()

    @property
    def active_tests(self):
        return [
            alert for alert
            in self
            if alert.is_active_test
        ]

    @property
    def planned_tests(self):
        return PlannedTests.from_yaml()

    @property
    def planned_tests_in_future(self):
        return [
            planned_test for planned_test
            in self.planned_tests
            if planned_test.is_planned
        ]

    @property
    def status_box_announcements(self):
        return [
            planned_test for planned_test
            in self.planned_tests_in_future
            if planned_test.display_in_status_box
        ]

    @property
    def planned_non_public_test_alerts(self):
        return [
            planned_test for planned_test
            in self.planned_tests_in_future
            if not planned_test.is_public
        ]

    @property
    def planned_grouped_by_date(self):
        alerts_by_date = defaultdict(list)
        for planned_test in self.planned_tests:
            if planned_test.is_planned:
                alerts_by_date[planned_test.starts_at_date.as_local_date].append(planned_test)
        return alerts_by_date.items()

    @property
    def planned_public_grouped_by_date(self):
        alerts_by_date = defaultdict(list)
        for planned_test in self.planned_tests:
            if planned_test.is_planned and planned_test.is_public:
                alerts_by_date[planned_test.starts_at_date.as_local_date].append(planned_test)
        return alerts_by_date.items()

    @property
    def planned_non_public_grouped_by_date(self):
        alerts_by_date = defaultdict(list)
        for planned_test in self.planned_tests:
            if planned_test.is_planned and not planned_test.is_public:
                alerts_by_date[planned_test.starts_at_date.as_local_date].append(planned_test)
        return alerts_by_date.items()

    @classmethod
    def load(cls, publish_timestamp_file=False, publish_healthcheck_filename=None):
        session = setup_boto3_session()
        s3 = session.client('s3')
        data = cls.from_yaml() + cls.from_api()
        alerts = []
        if publish_timestamp_file:
            # If `publish_timestamp_file` is True, with every alert from DB iterated through
            # the current timestamp will be written to `publish_healthcheck_filename` to
            # indicate an ongoing publish
            for alert_dict in data:
                start = time.time()
                if 'simple_polygons' not in alert_dict['areas'] or is_in_uk(alert_dict['areas']['simple_polygons']):
                    alerts.append(alert_dict)
                    put_timestamp_to_s3(publish_healthcheck_filename, s3)
                end = time.time()
                current_app.logger.info(f"Alert {alert_dict.get("id")} has taken {end - start} seconds to load")
        else:
            for alert_dict in data:
                if 'simple_polygons' not in alert_dict['areas'] or is_in_uk(alert_dict['areas']['simple_polygons']):
                    alerts.append(alert_dict)
        return cls(alerts)

    @classmethod
    def from_api(cls):
        return alerts_api_client.get_alerts()

    @classmethod
    def from_yaml(cls, path=REPO / 'data.yaml'):
        with path.open() as stream:
            return yaml.safe_load(stream)['alerts']
