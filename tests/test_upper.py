import os
from unittest import TestCase

import yaml
from six import print_
from toscaparser.tosca_template import ToscaTemplate

import requests_mock
from toskeriser.analyser import analyse_description
# from toskeriser.helper import CONST


class Test_Upper(TestCase):
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

    def start_test(self, force=False):
        with requests_mock.mock() as m:
            # register mock requests
            _base_par = 'size_gt=0&sort=stars&sort=pulls&sort=-size'
            for par, res in self._mock_responces.items():
                m.get('http://df.io/search?{}&{}'.format(_base_par, par),
                      json=res, complete_qs=True)

            # start the completation
            analyse_description(
                self._file_path, components=[], policy=None,
                constraints={}, interactive=False, force=force,
                df_host='http://df.io'
            )

        # check the result
        self._check_TOSCA(self._new_path)

    def _check_TOSCA(self, new_path):
        tosca = ToscaTemplate(new_path)
        self.assertIsNotNone(tosca)
        for node in tosca.nodetemplates:
            self.assertIn(node.name, self._node_templates)
            self.assertTrue(
                self._check_yaml(self._node_templates[node.name],
                                 node.entity_tpl))

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
