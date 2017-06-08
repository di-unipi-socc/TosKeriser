# TosKeriser

Tool to complete TosKer application description with suitable Docker Images.


## Usage
```
TosKeriser, a tool to complete TosKer application description with suitable Docker Images.

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
```
