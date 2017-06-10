import os
import requests
import requests_mock
import logging
import yaml
from unittest import TestCase
from six import print_
from toscaparser.tosca_template import ToscaTemplate

from toskeriser.helper import Logger, CONST
from toskeriser.analyser import _analyse_description as analyse


class Test_All(TestCase):

    @classmethod
    def setUpClass(self):
        self._file_path = 'toskeriser/tests/examples/example_all.yaml'
        self._new_path = 'toskeriser/tests/examples/example_all.completed.yaml'
        self._mock_responce = {
            'count': 1,
            'images': [
                {
                    'name': 'dannyedel/jekyll-with-extras:latest',
                    'softwares': [
                        {'software': 'node', 'ver': '6.2.1'},
                        {'software': 'ruby', 'ver': '2.2.1'},
                        {'software': 'wget', 'ver': '1.0.0'}
                    ],
                    'distro': 'Alpine Linux v3.4',
                    'size': 20000000,
                    'pulls': 200,
                    'stars': 23
                }
            ]
        }
        self._updated_yaml = yaml.load('''
              type: tosker.nodes.Container
              properties:
                  supported_sw:
                      node: 6.2.1
                      ruby: 2.2.1
                      wget: 1.0.0
                  os_distribution: Alpine Linux v3.4
              artifacts:
                  my_image:
                      file: dannyedel/jekyll-with-extras:latest
                      type: tosker.artifacts.Image
                      repository: docker_hub''')

    def setUp(self):
        try:
            os.remove(self._new_path)
        except FileNotFoundError:
            pass

    def tearDown(self):
        try:
            os.remove(self._new_path)
        except FileNotFoundError:
            pass

    def test_all_default(self):
        get_par = 'size_gt=0&'\
                  'sort=stars&sort=pulls&sort=-size&'\
                  'node=6.2&ruby=2&wget=&distro=alpine'

        with requests_mock.Mocker() as m:
            m.get('http://df.io/search?' + get_par, json=self._mock_responce)
            analyse(self._file_path, components=[], policy=None,
                    constraints={}, interactive=False, force=False,
                    df_host='http://df.io')

        self._check_TOSCA(self._new_path)

    def test_all_policy(self):
        def run(policy, q_policy):
            get_par = 'size_gt=0&'\
                      ''+q_policy+'&'\
                      'node=6.2&ruby=2&wget=&distro=alpine'

            with requests_mock.Mocker() as m:
                m.get('http://df.io/search?' + get_par, json=self._mock_responce)
                analyse(self._file_path, components=[], policy=policy,
                        constraints={}, interactive=False, force=False,
                        df_host='http://df.io')

            self._check_TOSCA(self._new_path)

        run(CONST.POLICY_TOP, 'sort=stars&sort=pulls&sort=-size')
        run(CONST.POLICY_SIZE, 'sort=-size&sort=stars&sort=pulls')
        run(CONST.POLICY_USED, 'sort=pulls&sort=stars&sort=-size')

    def test_all_constraints(self):
        get_par = 'pulls_gt=20&stars_lte=100&size_lt=1000000000&'\
                  'sort=stars&sort=pulls&sort=-size&'\
                  'node=6.2&ruby=2&wget=&distro=alpine'

        constraints = {'pulls': '>20', 'stars': '<=100', 'size': '<1GB'}
        with requests_mock.Mocker() as m:
            m.get('http://df.io/search?' + get_par, json=self._mock_responce)
            analyse(self._file_path, components=[], policy=None,
                    constraints=constraints, interactive=False, force=False,
                    df_host='http://df.io')

        self._check_TOSCA(self._new_path)

    def _check_TOSCA(self, new_path):
        tosca = ToscaTemplate(new_path)
        self.assertIsNotNone(tosca)
        node = next((node for node in tosca.nodetemplates
                     if node.name == 'server_container'))
        self.assertIsNotNone(node)

        self.assertTrue(self._check_yaml(self._updated_yaml, node.entity_tpl))

        node = next((node for node in tosca.nodetemplates
                     if node.name == 'server'))
        self.assertIsNotNone(node)
        self.assertEqual('server_container',
                         node.entity_tpl['requirements'][0]['host']['node'])

    def _check_yaml(self, a, b):
        if len(a) == len(b):
            if isinstance(a, list) and isinstance(b, list):
                return all(self._check_yaml(v, b[i]) for i, v in enumerate(a))
            elif isinstance(a, dict) and isinstance(b, dict):
                return all(k in b and self._check_yaml(v, b[k])
                           for k, v in a.items())
            else:
                return a == b
        else:
            return False
