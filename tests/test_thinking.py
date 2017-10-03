import yaml

from .test_upper import TestUpper


class TestThinking(TestUpper):

    @classmethod
    def setUpClass(self):
        self._file_path = 'data/examples/thinking-app/thinking.csar'
        self._new_path = 'data/examples/thinking-app/thinking.completed.csar'
        self._mock_responces = {
            'mvn=3&java=1.8&git=': {
                'count': 1,
                'images': [
                    {
                        'name': 'stephenreed/jenkins-java8-maven-git:latest',
                        'softwares': [
                            {'software': 'java', 'ver': '1.8.0'},
                            {'software': 'mvn', 'ver': '3.2.2'},
                            {'software': 'git', 'ver': '1.9.1'}
                        ],
                        'distro': 'Ubuntu 14.04.5 LTS',
                        'size': 20000000,
                        'pulls': 200,
                        'stars': 23
                    }
                ]
            },
            'node=6&npm=3&git=': {
                'count': 1,
                'images': [
                    {
                        'name': 'jekyll/jekyll:builder',
                        'softwares': [
                            {'software': 'node', 'ver': '6.9.5'},
                            {'software': 'npm', 'ver': '3.10.10'},
                            {'software': 'git', 'ver': '2.11.2'}
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
    api:
      type: tosker.nodes.Software
      requirements:
      - host:
          node_filter:
            properties:
            - ports:
              - 8080: {get_input: api_port}
            - supported_sw:
              - mvn: 3.x
              - java: 1.8.x
              - git: x
          node: api_container
      - connection: mongodb
      interfaces:
        Standard:
          create:
            implementation: scripts/api/install.sh
            inputs:
              repo: https://github.com/jacopogiallo/thoughts-api
              branch: {get_input: api_branch}
          configure:
            implementation: scripts/api/configure.sh
            inputs:
              dbURL: mongodb
              dbPort: 27017
              dbName: thoughtsSharing
              collectionName: thoughts
          start:
            implementation: scripts/api/start.sh
          stop:
            implementation: scripts/api/stop.sh
          delete:
            implementation: scripts/api/uninstall.sh

    gui:
      type: tosker.nodes.Software
      requirements:
      - host:
          node_filter:
            properties:
            - ports:
              - 3000: {get_input: gui_port}
            - supported_sw:
              - node: 6.x
              - npm: 3.x
              - git: x
          node: gui_container
      - dependency: api
      interfaces:
        Standard:
          create:
            implementation: scripts/gui/install.sh
            inputs:
              repo: https://github.com/jacopogiallo/thoughts-gui
              branch: {get_input: gui_branch}
          configure:
            implementation: scripts/gui/configure.sh
            inputs:
              apiUrl: localhost
              apiPort: {get_input: api_port}
              apiResource: thoughts
          start:
            implementation: scripts/gui/start.sh
          stop:
            implementation: scripts/gui/stop.sh
          delete:
            implementation: scripts/gui/uninstall.sh

    mongodb:
      type: tosker.nodes.Container
      artifacts:
        my_image:
          file: mongo:3.4
          type: tosker.artifacts.Image.Service
          repository: docker_hub
      requirements:
      - storage:
          node: dbvolume
          relationship:
            type: tosca.relationships.AttachesTo
            properties:
              location: /data/db

    dbvolume:
      type: tosker.nodes.Volume
    api_container:
      type: tosker.nodes.Container
      properties:
        supported_sw:
          java: 1.8.0
          mvn: 3.2.2
          git: 1.9.1
        os_distribution: Ubuntu 14.04.5 LTS
        ports:
          8080: {get_input: api_port}
      artifacts:
        my_image:
          file: stephenreed/jenkins-java8-maven-git:latest
          type: tosker.artifacts.Image
          repository: docker_hub
    gui_container:
      type: tosker.nodes.Container
      properties:
        supported_sw:
          npm: 3.10.10
          node: 6.9.5
          git: 2.11.2
        os_distribution: Alpine Linux v3.5
        ports:
          3000: {get_input: gui_port}
      artifacts:
        my_image:
          file: jekyll/jekyll:builder
          type: tosker.artifacts.Image
          repository: docker_hub
''')

    def test_all(self):
        self.start_test()
