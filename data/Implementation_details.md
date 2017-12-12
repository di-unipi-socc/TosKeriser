# Implementation Details
**Table of Contents**
* [Working schema](#working-schema)
  + [TOSCA parse](#tosca-parse)
  + [Validation](#validation)
  + [Filter](#filter)
  + [Merge](#merge)
  + [Complete](#complete)
* [Algorithms](#algorithms)

## Working schema
Toskeriser goes through the following set of steps, as it is also shown in the figure, to complete the imputed TOSCA representation of the application.
![toskerise pipeline](data/img/toskerise_pipeline.png)

### TOSCA parse
If the input is a CSAR the content is extracted. After that, the TOSCA YAML file is parsed and validated by using the `toscaparser` library by OpenStack.

### Validation
This phase validates that the `node_filter` and the `tosker.groups.DeploymentUnit` are defined as our specification, and that software required by a node are available on DockerFinder.

In particular the `tosker.groups.DeploymentUnit` has four constraints that must be checked:
- The groups must contain only nodes of type`tosker.nodes.Software`
- All the groups in the same `node_template` must be disjoint.
- All software component inside the group must have either a host requirement toward another member of the group or to the same container.
- The nodes of the group cannot be the target of host requirements of a software component that is not in the same group.

### Filter
This phase scan all the groups and all the nodes in order to find out what has to be completed. A node is considered eligible to be updated if it:
- is of type `tosker.nodes.Software`
- is a bottom component
- has a `host` require without a target node
- is selected to be updated, by default all nodes are selected

If the user uses the *force mode* the third constraint is removed.

Instead, a group is eligible to be updated if at least a node in the group is eligible to be updated.

The output of this phase is a set of tuples,  set of nodes and multi-set of constraints for each node.

### Merge
This phase merges, if possible, the multiset of constraints. The merge operation can return errors if same constraints specified different values, i.e. two different port mapping, two different os distribution. For what concern the `supported_sw` instead it is possible to find a suitable version for different version constraint of the same software, i.e. java:1.x e java:1.8.3 -> java:1.8.3.

### Complete
For all the tuple of the input set the following three phases are executed:
- *search images*, build and execute a query to DockerFinder by exploits the constraints, the policy, and the global constraints.
- *choose image*, among all the images returned by DockerFinder one image is selected by a function or by the user.
- *complete specification*, the TOSCA YAML specification is updated adding the new container and by updating the host requirements of all the node in the input set.

If it is not possible to find all the components the specification is updated anyway, but the user is notified.

## Algorithms
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
