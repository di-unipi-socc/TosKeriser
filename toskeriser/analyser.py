import re
import traceback

import ruamel.yaml
from six import print_, string_types
from toscaparser.common.exception import ValidationError
from toscaparser.tosca_template import ToscaTemplate

from . import completer, helper, merger
from .exceptions import TosKeriserException
from .helper import CONST, Logger

_log = None


def analyse_description(file_path, components=[], policy=None,
                        constraints={}, groups=[],
                        interactive=False, force=False,
                        df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    new_path = _gen_new_path(file_path, 'completed')
    try:
        if file_path.endswith(('.zip', '.csar', '.CSAR')):
            _log.debug('CSAR founded')
            csar_tmp_path, yaml_path = helper.unpack_csar(file_path)
            _update_tosca(yaml_path, yaml_path,
                          components, policy, constraints, groups,
                          interactive, force, df_host)
            helper.pack_csar(csar_tmp_path, new_path)
        else:
            _log.debug('YAML founded')
            _update_tosca(file_path, new_path,
                          components, policy, constraints, groups,
                          interactive, force, df_host)
    except ValidationError as e:
        raise TosKeriserException('Validation error:{}'.format(e))
    except TosKeriserException as e:
        raise e
    except Exception as e:
        print_('Internal error: {}'.format(e))
        _log.debug(traceback.format_exc())


def _gen_new_path(file_path, mod):
    points = file_path.split('.')
    return '{}.{}.{}'.format('.'.join(points[:-1]), mod, points[-1])


def _update_tosca(file_path, new_path,
                  components=[], policy=None, constraints={}, groups=[],
                  interactive=False, force=False, df_host=CONST.DF_HOST):
    # TODO: split this method
    _log.debug('update TOSCA YAML file {} to {}'.format(file_path, new_path))
    try:
        tosca = ToscaTemplate(file_path)
    except Exception as e:
        _log.error(e)

    _validate_node_filter(tosca)

    _check_components(tosca, components)

    with open(file_path, 'r') as f:
        tosca_yaml = ruamel.yaml.round_trip_load(f, preserve_quotes=True)

    errors = []
    to_complete = False

    already_analysed = []

    new_groups = _merge_groups(tosca.topology_template.groups, groups)
    _log.debug('merged_groups {}'.format(new_groups))

    class Group:

        def __init__(self, name, members):
            self.name = name
            self.members = members

    nodes_yaml = tosca_yaml['topology_template']['node_templates']
    for name, members in new_groups.items():
        group = Group(name,
                      [helper.get_node_from_tpl(tosca, m) for m in members])
        properties = []
        if any((_must_update(n, force, components) for n in group.members)):
            for m in group.members:
                already_analysed.append(m.name)
                properties.append(helper.get_host_node_filter(m))

            _log.debug('properties {}'.format(properties))
            merged_properties = merger.merge(properties)
            _log.debug('merged properties {}'.format(merged_properties))

            try:
                _log.debug('start completation of group {}'.format(group.name))
                completer.complete_group(group, merged_properties, nodes_yaml,
                                         policy, constraints, interactive,
                                         df_host)
                to_complete = True
            except TosKeriserException as e:
                errors += e.mgs

    # remove the node that are already processed as part of a group
    for node in (n for n in tosca.nodetemplates
                 if n.name not in already_analysed):
        if _must_update(node, force, components):
            to_complete = True
            _log.debug('node {.name} is abstract'.format(node))
            try:
                _log.debug('start completation of node {}'
                           ''.format(node.name))
                completer.complete(node, nodes_yaml, tosca,
                                   policy, constraints,
                                   interactive, df_host)
            except TosKeriserException as e:
                errors += e.stack

    if len(errors) == 0 and to_complete:
        _write_updates(tosca_yaml, new_path)
    elif len(errors) > 0:
        raise TosKeriserException(*errors)
    else:
        raise TosKeriserException('no abstract node founded')


def _check_components(tosca, components):
    if hasattr(tosca, 'nodetemplates'):
        if tosca.nodetemplates:
            for c in components:
                correct = False
                for n in tosca.nodetemplates:
                    if c == n.name:
                        correct = True
                if not correct:
                    raise TosKeriserException(
                        'component "{}" not founded'.format(c))


def _validate_node_filter(tosca):
    errors = []
    for node in tosca.nodetemplates:
        node_filter = helper.get_host_node_filter(node)
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


def _merge_groups(tosca_groups, cmd_groups):
    groups = {g.name: g.members for g in tosca_groups}
    groups.update(
        {'-'.join(members): members for members in cmd_groups}
    )
    _log.debug('groups before merge {}'.format(groups))
    keep = {name: True for name in groups.keys()}

    def merge(g1, g2):
        groups[g1] = list(set(groups[g1] + groups[g2]))
        groups[g2] = groups[g1]
        keep[g1] = True
        keep[g2] = False
        return g1

    for group in cmd_groups:
        to_merge = '-'.join(group)
        for member in group:
            groups_set = set([k for k in groups.keys()
                              if k != to_merge and keep[k]])
            while len(groups_set) > 0:
                name = groups_set.pop()
                members = groups[name]
                if member in members and to_merge != name:
                    if to_merge in groups_set:
                        groups_set.remove(to_merge)
                    to_merge = merge(name, to_merge)
                    _log.debug('merge {} with {}'.format(to_merge, name))
                    groups_set.add(to_merge)

    # _log.debug('keep {}'.format(keep))
    return {k: v for k, v in groups.items() if keep[k]}


def _must_update(node, force, components):
    def is_software(node):
        return True if node.type == CONST.SOFTWARE_TYPE else False

    def has_requirement_key(node, key):
        requirement = helper.get_host_requirements(node)
        if requirement is not None and isinstance(requirement, dict):
            if key in requirement and\
               requirement[key] is not None:
                return True
        return False

    def has_nodefilter(node):
        return has_requirement_key(node, 'node_filter')

    def has_node(node):
        return has_requirement_key(node, 'node') or\
            isinstance(helper.get_host_requirements(node), string_types)

    if is_software(node) and\
       (len(components) == 0 or node.name in components) and\
       (not has_node(node) or (force and has_nodefilter(node))):
        return True
    return False


def _write_updates(tosca, new_path):
    with open(new_path, 'w') as f:
        ruamel.yaml.round_trip_dump(tosca, f,
                                    # width=80,
                                    # indent=2,
                                    # block_seq_indent=2,
                                    # top_level_colon_align=True
                                    )
