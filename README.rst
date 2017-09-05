TosKeriser
==========

TosKeriser is a tool to complete
`TosKer <https://github.com/di-unipi-socc/TosKer>`__ applications with
suitable Docker Images. The user can specify the software required by
each component and the tool complete the specification with a suitable
container to run the components.

It was first presented in > *A. Brogi, D, Neri, L. Rinaldi, J. Soldani >
**From (incomplete) TOSCA specifications to running applications, with
Docker.** > Submitted for publication*

If you wish to reuse the tool or the sources contained in this
repository, please properly cite the above mentioned paper. Below you
can find the BibTex reference:

::

    @misc{TosKeriser,
      author = {Antonio Brogi and Davide Neri and Luca Rinaldi and Jacopo Soldani},
      title = {{F}rom (incomplete) {TOSCA} specifications to running applications, with {D}ocker,
      note = {{\em [Submitted for publication]}}
    }

Quick Guide
-----------

Installation
~~~~~~~~~~~~

In is possible to install TosKeriser by using pip:

::

    # pip install toskeriser

The minimum Python version supported is 2.7.

Example of usage
~~~~~~~~~~~~~~~~

For instance the following application has a components called
``server`` require a set of software (node>=6.2, ruby>2 and any version
of wget) and Alpine as Linux distribution.

::

    ...
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
      ...

After run TosKeriser on this specification, it creates the component
``server_container`` and connects the ``server`` component to it. It is
possible to see that the ``server_container`` has all the software
required by ``server`` and has also Alpine v3.4 as Linux distribution.

::

    ...
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
      ...

    server_container:
         type: tosker.nodes.Container
         properties:
           supported_sw:
             node: 6.2.0
             ash: 1.24.2
             wget: 1.24.2
             tar: 1.24.2
             bash: 4.3.42
             ruby: 2.3.1
             httpd: 1.24.2
             npm: 3.8.9
             git: 2.8.3
             erl: '2'
             unzip: 1.24.2
           os_distribution: Alpine Linux v3.4
         artifacts:
           my_image:
             file: jekyll/jekyll:3.1.6
             type: tosker.artifacts.Image
             repository: docker_hub

More examples can be found in the ``data/examples`` folder.

Usage guide
-----------

::

    toskerise FILE [COMPONENT..] [OPTIONS]
    toskerise --help|-h
    toskerise --version|-v

    FILE
      TOSCA YAML file or a CSAR to be completed

    COMPONENT
      a list of component to be completed (by default all component are considered)

    OPTIONS
      --debug                              active debug mode
      -q|--quiet                           active quiet mode
      -i|--interactive                     active interactive mode
      -f|--force                           force the update of all containers
      --constraints=value                  constraint to give to DockerFinder
                                           (e.g. --constraints 'size<=100MB pulls>30 stars>10')
      --policy=top_rated|size|most_used    ordering of the images

License
-------

MIT license
