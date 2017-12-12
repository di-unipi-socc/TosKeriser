# TosKeriser
[![pipy](https://img.shields.io/pypi/v/toskeriser.svg)](https://pypi.python.org/pypi/toskeriser)
[![travis](https://travis-ci.org/di-unipi-socc/TosKeriser.svg?branch=master)](https://travis-ci.org/di-unipi-socc/TosKeriser)

TosKeriser is a tool to complete [TosKer](https://github.com/di-unipi-socc/TosKer) applications with suitable Docker Images. The user can specify the software required by each component and the tool complete the specification with a suitable container to run the components.

It was first presented in
> _A. Brogi, D, Neri, L. Rinaldi, J. Soldani <br/>
> **From (incomplete) TOSCA specifications to running applications, with Docker.** <br/>
> Submitted for publication_

If you wish to reuse the tool or the sources contained in this repository, please properly cite the above mentioned paper. Below you can find the BibTex reference:
```
@misc{TosKeriser,
  author = {Antonio Brogi and Davide Neri and Luca Rinaldi and Jacopo Soldani},
  title = {{F}rom (incomplete) {TOSCA} specifications to running applications, with {D}ocker,
  note = {{\em [Submitted for publication]}}
}
```

## Table of Contents
- [Quick Guide](#quick-guide)
  * [Installation](#installation)
  * [Run specification with TosKer](#run-specification-with-tosker)
- [Example of specification](#example-of--specification)
- [Usage guide](#usage-guide)
- [License](#license)

## Quick Guide
### Installation
It is possible to install TosKeriser by using pip:
```
# pip install toskeriser
```
The minimum Python version supported is 2.7.

After the installation it is possible to download an example from the repository and run as follows:
```
wget https://github.com/di-unipi-socc/TosKeriser/blob/master/data/examples/thinking-app/thinking.csar?raw=true

toskerise thinking.csar --policy size
```
The complete specification will be on the file `thinking.completed.csar`.

### Run completed with TosKer
The specification completed with TosKeriser can than be given to [TosKer](https://github.com/di-unipi-socc/TosKer) which will manage the actual deployment.

First of all, install TosKer v1 with the following command:
```
# pip install 'tosker<2'
```

After the installation it is possible to run the application `thinking.completed` with the following command:
```
tosker thinking.completed.csar create start
```

Now thinking is deployed and it is possible to access it on the URL `http://localhost:8080`.

Instead to stop and delete the application run:
```
tosker thinking.completed.csar stop delete
```

## Example of specification
For instance the following application has a components called `server` require a set of software (node>=6.2, ruby>2 and any version of wget) and Alpine as Linux distribution.
```
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
```

After run TosKeriser on this specification, it creates the component `server_container` and connects the `server` component to it. It is possible to see that the `server_container` has all the software required by `server` and has also Alpine v3.4 as Linux distribution.

```
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
```

More examples can be found in the `data/examples` folder.

## Usage guide
```
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
```

## License

MIT license
