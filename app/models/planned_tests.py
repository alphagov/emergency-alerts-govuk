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
    environment = os.getenv('HOST', 'local')
    yaml_filename = (configs[environment].PLANNED_TESTS_YAML_FILE_NAME)

    @classmethod
    def from_yaml(cls, path=REPO / yaml_filename):
        data = yaml.safe_load(path.read_bytes())

        return cls(data['planned_tests'])
