import yaml

from .test_upper import TestUpper


class TestNoImage(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_no_image.yaml'
        self._new_path = 'data/examples/example_no_image.completed.yaml'
        self._mock_responces = {
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
app1:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
      node: app1_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app2:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
      node: app2_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app3:
  type: tosker.nodes.Software
  requirements:
  - host:
      node: app3_container
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
app2_container:
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
app3_container:
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

    def test_all(self):
        self.start_test()
