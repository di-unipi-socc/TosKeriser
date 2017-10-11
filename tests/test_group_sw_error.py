import yaml

from toskeriser.exceptions import TkStackException

from .test_upper import TestUpper


class TestGroupSwError(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_group_sw_error.yaml'
        self._new_path = 'data/examples/example_group_sw_error.completed.yaml'
        self._mock_responces = {}
        self._node_templates = yaml.load('')

    def test_default(self):
        # TODO: check the specific error
        with self.assertRaises(TkStackException):
            self._default_test()

    def test_policy(self):
        # TODO: check the specific error
        with self.assertRaises(TkStackException):
            self._policy_test()

    def test_constraints(self):
        # TODO: check the specific error
        with self.assertRaises(TkStackException):
            self._constraints_test()
