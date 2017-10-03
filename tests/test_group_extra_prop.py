import yaml
from .test_upper import TestUpper


class TestGroupExtraProp(TestUpper):
    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_group_extra_prop.yaml'
        self._new_path = 'data/examples/example_group_extra_prop.completed.yaml'
        self._mock_responces = {
            'node=6&npm=3&wget=&java=1.7&tar=&distro=debian': {
                'count': 1,
                'images': [
                    {
                        'name': 'webnicer/protractor-headless:latest',
                        'softwares': [
                            {'software': 'java', 'ver': '1.7.0'},
                            {'software': 'node', 'ver': '6.9.4'},
                            {'software': 'npm', 'ver': '3.10.10'},
                            {'software': 'wget', 'ver': '1.16'},
                            {'software': 'tar', 'ver': '1.27.1'}
                        ],
                        'distro': 'Debian GNU/Linux 8 (jessie)',
                        'size': 20000000,
                        'pulls': 200,
                        'stars': 23
                    }
                ]
            }
        }
        self._node_templates = yaml.load('''
app1:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - ports:
          - 8080: 80
        - env_variable:
          - TEST: 'hello'
        - supported_sw:
          - node: 6.x
          - npm: 3.x
          - wget: x
        - os_distribution: debian
      node: my_group_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh

app2:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - ports:
          - 4000: 23
        - env_variable:
          - TEST2: 'hellohello'
        - supported_sw:
          - java: 1.7.x
          - tar: x
      node: my_group_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh

my_group_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      java: 1.7.0
      npm: 3.10.10
      node: 6.9.4
      wget: '1.16'
      tar: 1.27.1
    os_distribution: Debian GNU/Linux 8 (jessie)
    ports:
      8080: 80
      4000: 23
    env_variable:
      TEST: hello
      TEST2: hellohello
  artifacts:
    my_image:
      file: webnicer/protractor-headless:latest
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_all(self):
        self.start_test()
