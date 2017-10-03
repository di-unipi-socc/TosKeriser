## v0.2.0 (03-09-2017):

Now is possible to require to pack more than one software in the same run-time environment (Docker container).

### Features
- Add a new group type `tosca.groups.DeploymentUnit`.

- Add group completion. All software components in the same group will be hosted on the same container. The constraints of all the members of the group will be automatically merged, if possible.

- Add a new command line parameter `--group=component1,...,componentN`. With this parameter, it is possible to specify new groups at run-time. The new groups will be automatically merged with the one present in the TOSCA specification.

- Add `node_filter` validity check. Now the user is notified if the TOSCA specification is not correct.

- New error handling system. During the execution, all the errors are collected and then returned to the user.

### Development
- Add new TOSCA example files

- Add new unittest

- Add Travis to the repo

### Bug
- Improve code stability and error check
