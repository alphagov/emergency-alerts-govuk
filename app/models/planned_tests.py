import yaml
from notifications_utils.serialised_model import SerialisedModelCollection

from app.models.planned_test import PlannedTest
from app.utils import REPO


class PlannedTests(SerialisedModelCollection):
    model = PlannedTest

    @classmethod
    def from_yaml(cls, path=REPO / 'planned-tests.yaml'):
        data = yaml.load(path.read_bytes(), Loader=yaml.CLoader)

        return cls(data['planned_tests'])
