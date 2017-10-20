import re

from toscaparser.nodetemplate import NodeTemplate

from . import helper, requester
from .exceptions import TkStackException
from .helper import CONST, Logger


def validate_groups(tosca, groups, force=False):
    # _log = Logger.get(__name__)

    def is_in_members(node, members):
        if isinstance(node, NodeTemplate):
            node = node.name
        return any((node == m.name for m in members))

    errors = []
    all_members = [m.name for g in groups for m in g.members]
    if len(set(all_members)) != len(all_members):
        errors.append('Groups are not disjoint. One or more component apper '
                      'in multiple groups')

    for group in groups:
        # add host to node
        for node in group.members:
            host_node = helper.get_host_node(node)
            node.host = helper.get_node_from_tpl(tosca, host_node)

        # search if same component are hosted on a container
        host_container = next((m.host for m in group.members
                               if m.host is not None and
                               m.host.type == CONST.CONTAINER_TYPE), None)

        for node in group.members:
            # check if all memeber of the group are software
            if node.type != CONST.SOFTWARE_TYPE:
                errors.append(
                    'Group "{}" has a member, "{}", that is not a software '
                    'component'.format(group.name, node.name))
                continue

            # check that if one member of the group has a host container all
            # have to have the same requirement
            if not force and host_container is not None:
                if node.host is None\
                   or (node.host.type == CONST.CONTAINER_TYPE
                       and node.host.name != host_container.name):
                    errors.append(
                        'Group "{0.name}", not all members are hosted on the '
                        '"{1.name}" container (use -f to exclude this check)'
                        ''.format(group, host_container))
                continue

            # check the member of the group do not require host to software
            # nodes outside the group
            if node.host is not None and node.host.type == CONST.SOFTWARE_TYPE:
                if not is_in_members(node.host.name, group.members):
                    errors.append(
                        'Node "{}",  member of the group "{}", requires a '
                        'host to a no member component, "{}"'
                        ''.format(node.name, group.name, node.host.name))

        # check if other software node require host to members of this group
        for node in tosca.nodetemplates:
            # if node is not member of the group
            if all((node.name != m.name for m in group.members)):
                host_node = helper.get_host_node(node)

                # if the node require to be hosted to a member of the group
                if host_node is not None and\
                   is_in_members(host_node, group.members):
                    errors.append(
                        'Node "{}" requires a host to a node member of '
                        'another group "{}"'
                        ''.format(node.name, group.name))
    if len(errors) > 0:
        raise TkStackException(*errors)


def validate_node_filter(tosca, df_host):
    _log = Logger.get(__name__)

    supported_sw = requester.get_software(df_host)
    _log.debug('software on DF {}'.format(supported_sw))

    errors = []
    for node in tosca.nodetemplates:
        node_filter = helper.get_host_nodefilter(node)
        if not isinstance(node_filter, list):
            errors.append('Node "{}": "node_filter" requires a list of '
                          'properties'.format(node.name))
            continue
        for n in node_filter:
            key, value = list(n.items())[0]
            if CONST.PROPERTY_OS == key:
                if not isinstance(value, str):
                    errors.append('Node "{}": property "{}" must be a string'
                                  '.'.format(node.name, CONST.PROPERTY_OS))
            elif CONST.PROPERTY_SW == key:
                if not isinstance(value, list):
                    errors.append('Node "{}": "{}" must be a list of software'
                                  ''.format(node.name, CONST.PROPERTY_SW))
                    continue
                for software in value:
                    s, v = list(software.items())[0]
                    if s not in supported_sw:
                        errors.append(
                            'Node "{}": software "{}" is not supported'
                            ''.format(node.name, s))
                    match = re.match('^([0-9]+.)*([0-9]+|x)?$', str(v))
                    if not isinstance(v, str) or match is None:
                        errors.append(
                            'Node "{}": software version "{}:{}" '
                            'must be a string with this pattern '
                            '([0-9].)*[0-9]+ or ([0-9].)*x '
                            '(i.e. 1.2.2, 1.2.x).'
                            ''.format(node.name, s, v))
            else:
                # TODO: check if other property are container one
                pass

    if len(errors) != 0:
        raise TkStackException(*errors)
