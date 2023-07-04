import os
from collections import defaultdict

import yaml
from emergency_alerts_utils.serialised_model import SerialisedModelCollection

from app.config import configs
from app.models.planned_test import PlannedTest
from app.utils import REPO


class PlannedTests(SerialisedModelCollection):
    model = PlannedTest
    planned_tests = defaultdict()
    environment = os.getenv('NOTIFY_ENVIRONMENT', 'development')
    yaml_filename = (configs[environment].PLANNED_TESTS_YAML_FILE_NAME)

    def __init__(self):
        self.planned_tests = self.from_yaml()

    @property
    def tests_in_future(self):
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
    def planned_non_public(self):
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
    def from_yaml(cls, path=REPO / yaml_filename):
        data = yaml.safe_load(path.read_bytes())

        return cls(data['planned_tests'])
