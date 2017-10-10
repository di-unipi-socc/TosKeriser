import re

from . import helper
from .helper import CONST, Logger
from .exceptions import TosKeriserException

_log = None


def validate_groups(tosca, groups):
    # TODO: check that both the tosca_groups and the cmd_groups are not overlapping with themselves

    global _log
    _log = Logger.get(__name__)

    def is_in_members(node, members):
        from toscaparser.nodetemplate import NodeTemplate
        if isinstance(node, NodeTemplate):
            node = node.name
        return any((node == m.name for m in members))

    errors = []
    for group in groups:
        if len(set([m.name for m in group.members])) != len(group.members):
            errors.append('Group "{}" members are repeted')

        for node in group.members:
            # check if all memeber of the group are software
            if node.type != CONST.SOFTWARE_TYPE:
                errors.append(
                    'Group "{}" has a member, "{}", that is not a software '
                    'component'.format(group.name, node.name))

            # check the member of the group do not require host to nodes
            # outside the group
            host_node = helper.get_host_node(node)
            if host_node is not None and\
               not is_in_members(host_node, group.members):
                errors.append(
                    'Node "{}",  member of the group "{}", requires a host to '
                    'a no member component, "{}"'
                    ''.format(node.name, group.name, host_node))

        # check if other node require host to members of this group
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
        raise TosKeriserException(*errors)


def validate_node_filter(tosca):
    global _log
    _log = Logger.get(__name__)

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
        raise TosKeriserException(*errors)
