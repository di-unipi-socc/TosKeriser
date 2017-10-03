import yaml
from .test_upper import Test_Upper


class Test_All(Test_Upper):
    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_group.yaml'
        self._new_path = 'data/examples/example_group.completed.yaml'
        self._mock_responces = {
            'node=6.2.0&ruby=2&wget=1&distro=alpine': {
                'count': 1,
                'images': [
                    {
                        'name': 'jekyll/jekyll:3.1.6',
                        'softwares': [
                            {'software': 'node', 'ver': '6.2.0'},
                            {'software': 'ruby', 'ver': '2.3.1'},
                            {'software': 'wget', 'ver': '1.24.2'}
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
app1:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - supported_sw:
          - node: 6.2.x
          - ruby: 2.x
          - wget: x
        - os_distribution: alpine
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
        - supported_sw:
          - node: 6.2.0
          - wget: 1.x
      node: my_group_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
my_group_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      node: 6.2.0
      wget: 1.24.2
      ruby: 2.3.1
    os_distribution: Alpine Linux v3.4
  artifacts:
    my_image:
      file: jekyll/jekyll:3.1.6
      type: tosker.artifacts.Image
      repository: docker_hub''')

    def test_all(self):
        self.start_test()
