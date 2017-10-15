import yaml

from toskeriser.exceptions import TkStackException

from .test_upper import TestUpper


class TestForceUpdate(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_force_update.yaml'
        self._new_path = 'data/examples/example_force_update.completed.yaml'
        self._mock_responces = {
            'node=6&ruby=2&distro=alpine': {
                'count': 1,
                'images': [
                    {
                        'name': 'jekyll/jekyll:builder',
                        'softwares': [
                            {'software': 'node', 'ver': '6.9.5'},
                            {'software': 'ruby', 'ver': '2.3.3'},
                            {'software': 'wget', 'ver': '1.25.1'}
                        ],
                        'distro': 'Alpine Linux v3.5',
                        'size': 20000000,
                        'pulls': 200,
                        'stars': 23
                    }
                ]
            },
            '': {
                'count': 1,
                'images': [
                    {
                        'name': 'gitlab/gitlab-ce:9.0.10-ce.0',
                        'softwares': [
                            {'software': 'perl', 'ver': '5.22.1'},
                            {'software': 'curl', 'ver': '7.53.0'},
                            {'software': 'nano', 'ver': '2.5.3'},
                            {'software': 'ruby', 'ver': '2.3.3'}
                        ],
                        'distro': 'Ubuntu 16.04.2 LTS',
                        'size': 20000000,
                        'pulls': 200,
                        'stars': 23
                    }
                ]
            }
        }
        self._node_templates = yaml.load('''
server:
  type: tosker.nodes.Software
  requirements:
  - host:
      node: server_container
      node_filter:
        properties:
        - supported_sw:
          - node: 6.x
          - ruby: 2.x
        - os_distribution: alpine
  interfaces:
    Standard:
      start:
        implementation: get_version.sh

server_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      ruby: 2.3.3
      node: 6.9.5
      wget: 1.25.1
    os_distribution: Alpine Linux v3.5
  artifacts:
    my_image:
      file: jekyll/jekyll:builder
      type: tosker.artifacts.Image
      repository: docker_hub

app1:
  type: tosker.nodes.Software
  requirements:
  - host:
      node: app1_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh

app1_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      perl: 5.22.1
      curl: 7.53.0
      nano: 2.5.3
      ruby: 2.3.3
    os_distribution: Ubuntu 16.04.2 LTS
  artifacts:
    my_image:
      file: gitlab/gitlab-ce:9.0.10-ce.0
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_default(self):
        with self.assertRaises(TkStackException):
            self._default_test()
        self._default_test(force=True)

    def test_policy(self):
        with self.assertRaises(TkStackException):
            self._policy_test()
        self._policy_test(force=True)

    def test_constraints(self):
        with self.assertRaises(TkStackException):
            self._constraints_test()
        self._constraints_test(force=True)
