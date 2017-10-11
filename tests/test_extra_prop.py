import yaml

from .test_upper import TestUpper


class TestExtraProp(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_extra_prop.yaml'
        self._new_path = 'data/examples/example_extra_prop.completed.yaml'
        self._mock_responces = {
            'node=6.2&ruby=2&distro=alpine': {
                'count': 1,
                'images': [
                    {
                        'name': 'jekyll/jekyll:3.1.6',
                        'softwares': [
                            {'software': 'node', 'ver': '6.2.0'},
                            {'software': 'ruby', 'ver': '2.3.1'},
                            {'software': 'ash', 'ver': '1.24.2'}
                        ],
                        'distro': 'Alpine Linux v3.4',
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
        - ports:
          - 8080: {get_input: asd}
          - 4000: 23
        - env_variable:
          - TEST: 'hello'
          - TEST2: {get_input: name}
        - supported_sw:
          - node: 6.2.x
          - ruby: 2.x
        - os_distribution: alpine
      node: server_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
server_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      node: 6.2.0
      ash: 1.24.2
      ruby: 2.3.1
    os_distribution: Alpine Linux v3.4
    ports:
      8080: {get_input: asd}
      4000: 23
    env_variable:
      TEST: 'hello'
      TEST2: {get_input: name}
  artifacts:
    my_image:
      file: jekyll/jekyll:3.1.6
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_default(self):
        self._default_test()

    def test_policy(self):
        self._policy_test()

    def test_constraints(self):
        self._constraints_test()
