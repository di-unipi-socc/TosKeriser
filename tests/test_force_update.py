import yaml

from toskeriser.exceptions import TosKeriserException

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
''')

    def test_all(self):
        with self.assertRaises(TosKeriserException):
            self.start_test()
        self.start_test(force=True)
