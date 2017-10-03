import yaml
from .test_upper import TestUpper

from toskeriser.exceptions import TosKeriserException


class TestGroupSwError(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_group_sw_error.yaml'
        self._new_path = 'data/examples/example_group_sw_error.completed.yaml'
        self._mock_responces = {}
        self._node_templates = yaml.load('')

    def test_all(self):
        with self.assertRaises(TosKeriserException):
            self.start_test()
