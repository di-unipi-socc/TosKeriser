import yaml

from .test_upper import TestUpper


class TestOnlyOs(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_only_os.yaml'
        self._new_path = 'data/examples/example_only_os.completed.yaml'
        self._mock_responces = {
            'distro=debian': {
                'count': 1,
                'images': [
                    {
                        'name': 'jwilder/nginx-proxy:latest',
                        'softwares': [],
                        'distro': 'Debian GNU/Linux 9 (stretch)',
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
      node_filter:
        properties:
        - os_distribution: debian
      node: server_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
server_container:
  type: tosker.nodes.Container
  properties:
    os_distribution: Debian GNU/Linux 9 (stretch)
  artifacts:
    my_image:
      file: jwilder/nginx-proxy:latest
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_default(self):
        self._default_test()

    def test_policy(self):
        self._policy_test()

    def test_constraints(self):
        self._constraints_test()
