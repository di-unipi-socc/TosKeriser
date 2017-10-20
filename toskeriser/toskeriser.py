import traceback

import ruamel.yaml
# from six import print_
from toscaparser.common.exception import ValidationError
from toscaparser.tosca_template import ToscaTemplate

from . import completer, helper, merger, requester, validator
from .exceptions import TkException, TkStackException
from .helper import CONST, Logger

_log = None


def toskerise(file_path, components=[], policy=None, constraints={},
              interactive=False, force=False, df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    is_csar = file_path.endswith(('.zip', '.csar', '.CSAR'))
    _log.debug('CSAR founded: {}'.format(is_csar))

    def get_new_path(partial):
        def gen_new_path(mod):
            points = file_path.split('.')
            return '{}.{}.{}'.format('.'.join(points[:-1]), mod, points[-1])
        return gen_new_path('partial') \
            if partial else\
            gen_new_path('completed')

    try:
        if is_csar:
            # extract CSAR
            csar_tmp_path, yaml_path = helper.unpack_csar(file_path)
            # process TOSCA
            is_partial, tosca_yaml = _process_tosca(yaml_path, components,
                                                    policy, constraints,
                                                    interactive, force,
                                                    df_host)
            # write changes
            _write_updates(tosca_yaml, yaml_path)
            # pack CSAR
            helper.pack_csar(csar_tmp_path, get_new_path(is_partial))
        else:
            # process TOSCA
            is_partial, tosca_yaml = _process_tosca(file_path, components,
                                                    policy, constraints,
                                                    interactive, force,
                                                    df_host)
            # write changes
            _write_updates(tosca_yaml, get_new_path(is_partial))
    except ValidationError as e:
        raise TkStackException('Validation error:{}'.format(e))
    except TkStackException as e:
        raise e
    except Exception as e:
        _log.debug(traceback.format_exc())
        raise TkException('Internal error: {}'.format(e))


def software_list(df_host):
    return sorted(requester.get_software(df_host))


def _process_tosca(file_path, components=[], policy=None, constraints={},
                   interactive=False, force=False, df_host=CONST.DF_HOST):
    # parse TOSCA
    tosca = ToscaTemplate(file_path)

    # Check TOSCA dependent input
    _check_components(tosca, components)

    # validation
    validator.validate_node_filter(tosca, df_host)
    groups = helper.convert_tosca_group(tosca)
    validator.validate_groups(tosca, groups, force)

    # filter and merge
    to_complete = _filter_and_merge(tosca, groups, force, components)
    if len(to_complete) == 0:
        raise TkStackException('no abstract node founded')

    # get yaml to be updated
    tosca_yaml = _get_roundtrip_node(file_path)
    node_yaml = tosca_yaml['topology_template']['node_templates']

    errors = []
    all_completed = True
    for component in to_complete:
        try:
            _log.debug('start completation of {}'.format(component.name))
            all_completed &= completer.complete(component, node_yaml, tosca,
                                                policy, constraints,
                                                interactive, df_host)
        except TkStackException as e:
            errors += e.stack

    if len(errors) > 0:
        raise TkStackException(*errors)

    return not all_completed, tosca_yaml


def _filter_and_merge(tosca, groups, force, components):
    '''
    Filter the groups and the nodes and returning a list of components
    to be update.
    '''
    already_analysed = []
    errors = []
    to_update = []

    for group in groups:
        constraints = []

        group_to_complete = False
        for m in group.members:
            m.to_update = _must_update(m, force, components)
            group_to_complete = m.to_update
            already_analysed.append(m.name)
            constraints.append(helper.get_host_nodefilter(m))

        if group_to_complete:
            try:
                group.constraints = merger.merge_constraint(constraints)
                _log.debug('merged properties {}'.format(group.constraints))
                to_update.append(group)
            except TkStackException as e:
                errors += e.stack

    # remove the node that are already processed as part of a group
    for node in (n for n in tosca.nodetemplates
                 if n.name not in already_analysed):
        if _must_update(node, force, components):
            _log.debug('node {.name} is abstract'.format(node))
            node.constraints = helper.get_host_nodefilter(node)
            to_update.append(node)

    if len(errors) != 0:
        raise TkStackException(*errors)
    return to_update


def _must_update(node, force, components):
    '''
    Check if a node has to be update.
    '''
    def is_software(node):
        return True if node.type == CONST.SOFTWARE_TYPE else False

    def has_requirement_key(node, key):
        return helper.get_host_key(node, key) is not None

    def has_nodefilter(node):
        return has_requirement_key(node, 'node_filter')

    def has_node(node):
        return helper.get_host_node(node) is not None

    if is_software(node) and\
       (len(components) == 0 or node.name in components) and\
       (not has_node(node) or force):
        return True
    return False


def _get_roundtrip_node(file_path):
    with open(file_path, 'r') as f:
        tosca_yaml = ruamel.yaml.round_trip_load(f, preserve_quotes=True)
    return tosca_yaml


def _write_updates(tosca, new_path):
    with open(new_path, 'w') as f:
        ruamel.yaml.round_trip_dump(tosca, f,
                                    # width=80,
                                    # indent=2,
                                    # block_seq_indent=2,
                                    # top_level_colon_align=True
                                    )


def _check_components(tosca, components):
    if hasattr(tosca, 'nodetemplates'):
        if tosca.nodetemplates:
            for c in components:
                correct = False
                for n in tosca.nodetemplates:
                    if c == n.name:
                        correct = True
                if not correct:
                    raise TkStackException(
                        'component "{}" not founded'.format(c))
