import yaml

from toskeriser.exceptions import TosKeriserException

from .test_upper import TestUpper


class TestNoUpdate(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_no_update.yaml'
        self._new_path = 'data/examples/example_no_update.completed.yaml'
        self._mock_responces = {}
        self._node_templates = yaml.load('')

    def test_all(self):
        # TODO: check the specific error
        with self.assertRaises(TosKeriserException):
            self.start_test()
        # TODO: check the specific error
        with self.assertRaises(TosKeriserException):
            self.start_test(force=True)
