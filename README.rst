TosKeriser
==========

TosKeriser is a tool for automatically completing TOSCA application
specifications, which can automatically discover the Docker-based
runtime environments that provide the software support needed by the
application components.

Users can specify the components forming an application, as well as the
software distributions they require by exploiting a predefined set of
`TOSCA types <https://di-unipi-socc.github.io/tosker-types/>`__. They
can then run TosKeriser, which will complete the specification with the
Docker containers offering the software needed by (groups of)
components. Obtained specification can then be run with
`TosKer <https://github.com/di-unipi-socc/TosKer>`__.

TosKeriser was first presented in > *A. Brogi, D, Neri, L. Rinaldi, J.
Soldani >*\ **From (incomplete) TOSCA specifications to running
applications, with Docker.**\ * > In: A. Cerone and M. Roveri (eds.),
SEFM 2017 Workshops. LNCS, Springer [In press]*

If you wish to reuse the tool or the sources contained in this
repository, please properly cite the above mentioned paper. Below you
can find the BibTex reference:

::

   @inproceedings{TosKeriser,
     author = {Antonio Brogi and Davide Neri and Luca Rinaldi and Jacopo Soldani},
     title = {{F}rom (incomplete) {TOSCA} specifications to running applications, with {D}ocker},
     editor = {A. Cerone and M. Roveri (eds.)}, 
     booktitle = {SEFM 2017 Workshops},
     series = {LNCS}, 
     publisher = {Springer},
     note = {{\em [In press]}}
   }

Table of Contents
-----------------

-  `Quick Guide <#quick-guide>`__

   -  `Installation <#installation>`__
   -  `Example of run of TosKeriser <#example-of-run-of-toskeriser>`__
   -  `Running completed specifications with
      TosKer <#running-completed-specifications-with-tosker>`__

-  `Example of to-be-completed
   specifications <#example-of-to-be-completed-specifications>`__
-  `Usage guide <#usage-guide>`__
-  `License <#license>`__

Quick Guide
-----------

Installation
~~~~~~~~~~~~

TosKeriser can be installed by using pip:

::

   # pip install toskeriser

(It requires Python version 2.7 or later).

Example of run of TosKeriser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of (incomplete) specifications are available in the
`data/examples <https://github.com/di-unipi-socc/TosKeriser/tree/master/data/examples>`__
folder.

To run TosKeriser to complete one of them, one just needs to download
one of them:

::

   curl -LO https://github.com/di-unipi-socc/TosKeriser/raw/master/data/examples/thinking-app/thinking.csar

and to run TosKeriser on the downloaded file:

::

   toskerise thinking.csar --policy size

The completed specification will be contained in
``thinking.completed.csar``.

Running completed specifications with TosKer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifications completed with TosKeriser can than be given to
`TosKer <https://github.com/di-unipi-socc/TosKer>`__, which will manage
their actual deployment.

First of all, install TosKer v1 with the following command:

::

   # pip install 'tosker<2'

After the installation it is possible to run the application
``thinking.completed.csar`` with the following command:

::

   tosker thinking.completed.csar create start

As a result, a concrete instance of the application is deployed, and it
can be accessed at ``http://localhost:8080``.

Instead, to stop and delete the application run:

::

   tosker thinking.completed.csar stop delete

Example of to-be-completed specifications
-----------------------------------------

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
   toskerise --supported_sw|-s
   toskerise --version|-v
   toskerise --help|-h

   FILE
     TOSCA YAML file or a CSAR to be completed

   COMPONENT
     a list of the components to be completed (by default all component are considered)

   OPTIONS
     -i|--interactive                     active interactive mode
     --policy=top_rated|size|most_used    ordering of the images
     -q|--quiet                           active quiet mode
     -f|--force                           force the update of all containers
     --constraints=value                  constraint to give to DockerFinder
                                          (e.g. --constraints 'size<=99MB pulls>30
                                                               stars>10')
     --debug                              active debug mode

License
-------

MIT license
