import yaml

from .test_upper import TestUpper


class TestPartial(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_partial.yaml'
        self._new_path = 'data/examples/example_partial.partial.yaml'
        self._mock_responces = {
            'node=6.2&npm=3&ruby=2&java=1.8&wget=&distro=ubuntu': {
                'count': 0,
                'images': []
            },
            'node=6&npm=&wget=1': {
                      'count': 1,
                      'images': [
                          {
                              'name': 'jekyll/jekyll:builder',
                              'softwares': [
                                  {'software': 'node', 'ver': '6.9.5'},
                                  {'software': 'wget', 'ver': '1.25.1'},
                                  {'software': 'ruby', 'ver': '2.3.3'},
                                  {'software': 'npm', 'ver': '3.10.10'}
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
app1:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - supported_sw:
          - node: 6.2.x
          - npm: 3.x
          - ruby: 2.x
          - java: 1.8.x
          - wget: x
        - os_distribution: ubuntu
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
          - node: 6.x
          - npm: x
          - wget: 1.x
      node: app2_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app2_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      ruby: 2.3.3
      npm: 3.10.10
      node: 6.9.5
      wget: 1.25.1
    os_distribution: Alpine Linux v3.5
  artifacts:
    my_image:
      file: jekyll/jekyll:builder
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_default(self):
        self._default_test()

    def test_policy(self):
        self._policy_test()

    def test_constraints(self):
        self._constraints_test()
