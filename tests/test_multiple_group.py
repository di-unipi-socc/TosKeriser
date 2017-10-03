import yaml
from .test_upper import TestUpper


class TestMultipleGroup(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/example_multiple_group.yaml'
        self._new_path = 'data/examples/example_multiple_group.completed.yaml'
        self._mock_responces = {
            'node=6.2&npm=3&ruby=2&wget=1&distro=alpine': {
                'count': 1,
                'images': [
                    {
                        'name': 'jekyll/jekyll:3.1.6',
                        'softwares': [
                            {'software': 'node', 'ver': '6.2.0'},
                            {'software': 'wget', 'ver': '1.24.2'},
                            {'software': 'ruby', 'ver': '2.3.1'},
                            {'software': 'npm', 'ver': '3.8.9'}
                        ],
                        'distro': 'Alpine Linux v3.4',
                        'size': 20000000,
                        'pulls': 200,
                        'stars': 23
                    }
                ]
            },
            'node=5&git=1&perl=5&curl=&java=1.7&unzip=&distro=ubuntu': {
                'count': 1,
                'images': [
                    {
                        'name': 'agileek/ionic-framework:2.0.0',
                        'softwares': [
                            {'software': 'java', 'ver': '1.7.0'},
                            {'software': 'perl', 'ver': '5.18.2'},
                            {'software': 'curl', 'ver': '7.35.0'},
                            {'software': 'node', 'ver': '5.6.0'},
                            {'software': 'git', 'ver': '1.9.1'},
                            {'software': 'unzip', 'ver': '6.00'}
                        ],
                        'distro': 'Ubuntu 14.04.4 LTS',
                        'size': 20000000,
                        'pulls': 200,
                        'stars': 23
                    }
                ]
            },
            'erl=&ruby=2&unzip=': {
                'count': 1,
                'images': [
                    {
                        'name': 'gitlab/gitlab-ce:9.0.10-ce.0',
                        'softwares': [
                            {'software': 'erl', 'ver': '2'},
                            {'software': 'unzip', 'ver': '6.00'},
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
        - supported_sw:
          - node: 6.2.x
          - npm: 3.x
          - ruby: 2.x
          - wget: x
        - os_distribution: alpine
      node: group1_container
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
      node: group1_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app3:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - supported_sw:
          - node: 5.x
          - git: 1.x
      node: group2_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app4:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - supported_sw:
          - perl: 5.x
          - curl: x
        - os_distribution: ubuntu
      node: group2_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app5:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - supported_sw:
          - java: 1.7.x
          - unzip: x
      node: group2_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
app6:
  type: tosker.nodes.Software
  requirements:
  - host:
      node_filter:
        properties:
        - supported_sw:
          - erl: x
          - ruby: 2.x
          - unzip: x
      #  - os_distribution: debian
      node: app6_container
  interfaces:
    Standard:
      start:
        implementation: get_version.sh
group1_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      node: 6.2.0
      wget: 1.24.2
      ruby: 2.3.1
      npm: 3.8.9
    os_distribution: Alpine Linux v3.4
  artifacts:
    my_image:
      file: jekyll/jekyll:3.1.6
      type: tosker.artifacts.Image
      repository: docker_hub
group2_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      java: 1.7.0
      perl: 5.18.2
      curl: 7.35.0
      node: 5.6.0
      git: 1.9.1
      unzip: '6.00'
    os_distribution: Ubuntu 14.04.4 LTS
  artifacts:
    my_image:
      file: agileek/ionic-framework:2.0.0
      type: tosker.artifacts.Image
      repository: docker_hub
app6_container:
  type: tosker.nodes.Container
  properties:
    supported_sw:
      ruby: 2.3.3
      erl: '2'
      unzip: '6.00'
    os_distribution: Ubuntu 16.04.2 LTS
  artifacts:
    my_image:
      file: gitlab/gitlab-ce:9.0.10-ce.0
      type: tosker.artifacts.Image
      repository: docker_hub
''')

    def test_all(self):
        # from toskeriser.helper import Logger
        # Logger.set_logger()
        self.start_test()
