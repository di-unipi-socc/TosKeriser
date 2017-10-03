import yaml
from .test_upper import TestUpper


class TestOnlySw(TestUpper):
    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_only_sw.yaml'
        self._new_path = 'data/examples/example_only_sw.completed.yaml'
        self._mock_responces = {
            'node=6&ruby=2': {
                'count': 1,
                'images': [
                    {
                        'name': 'jekyll/jekyll:builder',
                        'softwares': [
                          {'software': 'ruby', 'ver': '2.3.3'},
                          {'software': 'httpd', 'ver': '1.25.1'},
                          {'software': 'npm', 'ver': '3.10.10'},
                          {'software': 'node', 'ver': '6.9.5'},
                          {'software': 'wget', 'ver': '1.25.1'},
                          {'software': 'ash', 'ver': '1.25.1'},
                          {'software': 'git', 'ver': '2.11.2'},
                          {'software': 'bash', 'ver': '4.3.46'},
                          {'software': 'erl', 'ver': '2'},
                          {'software': 'unzip', 'ver': '1.25.1'},
                          {'software': 'tar', 'ver': '1.25.1'},
                        ],
                        'distro': '',
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
          - node: 6.x
          - ruby: 2.x
      node: server_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
server_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      ruby: 2.3.3
      httpd: 1.25.1
      npm: 3.10.10
      node: 6.9.5
      wget: 1.25.1
      ash: 1.25.1
      git: 2.11.2
      bash: 4.3.46
      erl: '2'
      unzip: 1.25.1
      tar: 1.25.1
  artifacts:
    my_image:
      file: jekyll/jekyll:builder
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_all(self):
        self.start_test()
