import os
import sys
import traceback
from unittest import TestCase

import requests_mock
import yaml
from six import StringIO, print_

from toskeriser import helper
from toskeriser.toskeriser import toskerise
from toskeriser.helper import CONST
from toskeriser.exceptions import TkException


class TestUpper(TestCase):

    @classmethod
    def setUpClass(self):
        self._file_path = ''
        self._new_path = ''
        self._mock_responces = {}
        self._node_templates = yaml.load()

    def setUp(self):
        try:
            os.remove(self._new_path)
        except OSError:
            pass

    # def tearDown(self):
    #     try:
    #         os.remove(self._new_path)
    #     except OSError:
    #         pass

    def _default_test(self, force=False):
        _base_par = 'size_gt=0&sort=stars&sort=pulls&sort=-size'
        self._test(_base_par, force=force)

    def _policy_test(self, force=False):
        def run(policy, q_policy):
            get_par = 'size_gt=0&' + q_policy
            self._test(get_par, policy=policy, force=force)

        run(CONST.POLICY_TOP, 'sort=stars&sort=pulls&sort=-size')
        run(CONST.POLICY_SIZE, 'sort=-size&sort=stars&sort=pulls')
        run(CONST.POLICY_USED, 'sort=pulls&sort=stars&sort=-size')

    def _constraints_test(self, force=False):
        get_par = 'size_gt=0&pulls_gt=20&stars_lte=100&size_lt=1000000000&'\
                  'sort=stars&sort=pulls&sort=-size'

        constraints = {'pulls': '>20', 'stars': '<=100', 'size': '<1GB'}
        self._test(get_par, constraints=constraints, force=force)

    def _test(self, base_par, policy=None, constraints={}, force=False):
        with requests_mock.mock() as m:
            # register mock requests
            for par, res in self._mock_responces.items():
                m.get('http://df.io/search?{}&{}'.format(base_par, par),
                      json=res, complete_qs=True)

            # start the completation
            sys.stdout, old_stdout = StringIO(), sys.stdout
            try:
                toskerise(
                    self._file_path, components=[], policy=policy,
                    constraints=constraints, interactive=False, force=force,
                    df_host='http://df.io'
                )

                # check the result
                if self._new_path.endswith('.csar'):
                    _, self._new_path = helper.unpack_csar(self._new_path)

                self._check_TOSCA(self._new_path)
            except TkException as e:
                sys.stdout = old_stdout
                print_(e, traceback.format_exc())
                self.assertTrue(False)
            sys.stdout = old_stdout

    def _check_TOSCA(self, new_path):
        # tosca = ToscaTemplate(new_path)
        with open(new_path) as tosca_file:
            tosca = yaml.load(tosca_file)

        self.assertIsNotNone(tosca)

        for name, node in tosca['topology_template']['node_templates'].items():
            self.assertIn(name, self._node_templates)
            self.assertTrue(
                self._check_yaml(self._node_templates[name],
                                 node))

    def _check_yaml(self, a, b):
        def track(value):
            if not value:
                print_('yaml do not match:\n{}\n{}'.format(a, b))
            return value

        if type(a) != type(b):
            return track(False)

        if isinstance(a, list) and isinstance(b, list):
            return track(
                all(self._check_yaml(v, b[i]) for i, v in enumerate(a))
            )
        elif isinstance(a, dict) and isinstance(b, dict):
            return track(
                all(k in b and self._check_yaml(v, b[k])
                    for k, v in a.items())
            )
        return track(a == b)
