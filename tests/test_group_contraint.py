import yaml

from toskeriser.exceptions import TosKeriserException

from .test_upper import TestUpper


class TestGroupOsError(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_group_constraint.yaml'
        self._new_path = 'data/examples/example_group_constraint.completed.yaml'
        self._mock_responces = {}
        self._node_templates = yaml.load('')

    def test_all(self):
        # TODO: check the specific error
        # from toskeriser.helper import Logger
        # Logger.set_logger()
        with self.assertRaises(TosKeriserException):
            self.start_test()
