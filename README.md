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

## Quick Guide
### Installation
In is possible to install TosKeriser by using pip:
```
# pip install toskeriser
```
The minimum Python version supported is 2.7.

### Example of usage
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


## Deployment Details
### Working schema
Toskeriser goes through the following set of steps, as it is also shown in the figure, to complete the imputed TOSCA representation of the application.
![toskerise pipeline](data/img/toskerise_pipeline.png)

#### TOSCA parse
If the input is a CSAR the content is extracted. After that, the TOSCA YAML file is parsed and validated by using the `toscaparser` library by OpenStack.

#### Validation
This phase validates that the `node_filter` and the `tosker.groups.DeploymentUnit` are defined as our specification, and that software required by a node are available on DockerFinder.

In particular the `tosker.groups.DeploymentUnit` has four constraints that must be checked:
- The groups must contain only nodes of type`tosker.nodes.Software`
- All the groups in the same `node_template` must be disjoint.
- The nodes inside the group cannot have host requirements towards a node that is not in the same groups.
- The nodes of the group cannot be the target of host requirements of a node that is not in the same group.

#### Filter
This phase scan all the groups and all the nodes in order to find out what has to be completed. A node is considered eligible to be updated if it:
- is of type `tosker.nodes.Software`
- has a `host` require without a target node
- is selected to be updated, by default all nodes are selected

If the user uses the *force mode* the second constraint is eliminated.

Instead, a group is eligible to be updated if at least a node in the group is eligible to be updated.

The output of this phase is a set of tuples,  set of nodes and multi-set of constraints for each node.

#### Merge
This phase merges, if possible, the multiset of constraints. The merge operation can return errors if same constraints specified different values, i.e. two different port mapping, two different os distribution. For what concern the `supported_sw` instead it is possible to find a suitable version for different version constraint of the same software, i.e. java:1.x e java:1.8.3 -> java:1.8.3.

#### Complete
For all the tuple of the input set the following three phases are executed:
- *search images*, build and execute a query to DockerFinder by exploits the constraints, the policy, and the global constraints.
- *choose image*, among all the images returned by DockerFinder one image is selected by a function or by the user.
- *complete specification*, the TOSCA YAML specification is updated adding the new container and by updating the host requirements of all the node in the input set.

If it is not possible to find all the components the specification is updated anyway, but the user is notified.

### Algorithms
**Must update**
```
input: component:string, components:array, force:boolean
output: boolean

if ¬is_software(component)
  return false;
if length(components) ≠ 0 ∧ component ∉ components
  return false;
if has_host_node(node) ∧ (¬force or ¬has_node_filter(node))
  return false
return true;
```

**Merge constraints**
```
input: nodes_constraints:array
output: hashmap

merged_constraints ← hashmap();

∀ constraints ∈ nodes_constraints {
  ∀ constraint ∈ constraints {
    if constraint is 'supported_sw'{
      ∀ software in constraint {
        if software ∈ merged_constraints
          merge_software(software, merged_constraints[software]);
        else
          add(software, merged_constraints);
      }
    } else {
      if constraints ∉ merged_constraints
        add(constraints, merged_constraints);
    }
  }
}

return merged_properties;
```

**Merge software**
```
input: version1:array, version2:array
output: array

i ← 0;
min_length ← min(length(version1), length(version2));
merged_version ← array();

while i < min_length ∧ v1[i] ≠ 'x' ∧ v2[i] ≠ 'x' {
  if v1[i] = v2[i]
    push(v1[i], merged_version);
  else
    return Nil;
  i ← i + 1;
}

if i < length(v1) ∧ v1[i] = 'x'
  return merged_version ∪ v2[i:];
else if i < length(v2) ∧ v2[i] = 'x'
  return merged_version ∪ v1[i:]
else if length(v1) ≠ length(v2)
  return Nil;
else
  return merged_version;
```

## License

MIT license
