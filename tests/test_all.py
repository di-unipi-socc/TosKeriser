import yaml

from .test_upper import TestUpper


class TestAll(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_all.yaml'
        self._new_path = 'data/examples/example_all.completed.yaml'
        self._mock_responces = {
            'node=6.2&ruby=2&wget=&distro=alpine': {
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
        }
        self._node_templates = yaml.load('''
server:
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
     node: server_container
  interfaces:
    Standard:
     start:
       implementation: get_version.sh
server_container:
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
      repository: docker_hub
''')

    def test_all(self):
        self.start_test()
