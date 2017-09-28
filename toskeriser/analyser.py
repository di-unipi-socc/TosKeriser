import traceback
# from os import path

from six import print_, string_types
from toscaparser.common.exception import ValidationError
from toscaparser.tosca_template import ToscaTemplate
import ruamel.yaml

from . import completer, helper, merger
from .helper import CONST, Logger

_log = None


def analyse_description(file_path, components=[], policy=None,
                        constraints={}, interactive=False, force=False,
                        df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    try:
        _analyse_description(file_path, components, policy, constraints,
                             interactive, force, df_host)
    except ValidationError as e:
        print_('Validation error:{}'.format(e))
    except Exception as e:
        _log.error('error type: {}, error: {}'.format(type(e), e))
        _log.debug(traceback.format_exc())
        print_('ERRORS:\n- {}'.format('\n- '.join(e.args)))


def _analyse_description(file_path, components=[], policy=None,
                         constraints={}, interactive=False, force=False,
                         df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    if file_path.endswith(('.zip', '.csar', '.CSAR')):
        _log.debug('CSAR founded')
        csar_tmp_path, yaml_path = helper.unpack_csar(file_path)
        _update_tosca(yaml_path, yaml_path,
                      components, policy,
                      constraints, interactive,
                      force, df_host)
        new_path = _gen_new_path(file_path, 'completed')
        helper.pack_csar(csar_tmp_path, new_path)
    else:
        _log.debug('YAML founded')
        new_path = _gen_new_path(file_path, 'completed')
        _update_tosca(file_path, new_path,
                      components, policy,
                      constraints, interactive,
                      force, df_host)


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
    with open(new_path, "w") as f:
        ruamel.yaml.round_trip_dump(tosca, f,
                                    # width=80,
                                    # indent=2,
                                    # block_seq_indent=2,
                                    # top_level_colon_align=True
                                    )


def _gen_new_path(file_path, mod):
    points = file_path.split('.')
    return '{}.{}.{}'.format('.'.join(points[:-1]), mod, points[-1])


def _check_components(tosca, components):
    if hasattr(tosca, 'nodetemplates'):
        if tosca.nodetemplates:
            for c in components:
                correct = False
                for n in tosca.nodetemplates:
                    if c == n.name:
                        correct = True
                if not correct:
                    raise Exception('component "{}" not founded'.format(c))


def _update_tosca(file_path, new_path,
                  components=[], policy=None,
                  constraints={}, interactive=False, force=False,
                  df_host=CONST.DF_HOST):
    _log.debug('update TOSCA YAML file {} to {}'.format(file_path, new_path))

    try:
        tosca = ToscaTemplate(file_path)
    except Exception as e:
        _log.error(e)

    _validate_node_filter(tosca)

    _check_components(tosca, components)

    tosca_yaml = ruamel.yaml.round_trip_load(open(file_path),
                                             preserve_quotes=True)
    errors = []
    to_complete = False

    # DEBUG
    # for g in tosca.topology_template.groups:
    #     _log.debug(g.name)
    #     for m in g.members:
    #         _log.debug(m)
    # END DEBUG

    already_analysed = []

    nodes_yaml = tosca_yaml['topology_template']['node_templates']
    for g in tosca.topology_template.groups:
        properties = []
        members = [helper.get_node_from_tpl(tosca, m) for m in g.members]
        if any((_must_update(n, force, components) for n in members)):
            for m in members:
                already_analysed.append(m.name)
                properties.append(helper.get_host_node_filter(m))

            _log.debug('properties {}'.format(properties))
            merged_properties = merger.merge(properties)
            _log.debug('merged properties {}'.format(merged_properties))

            try:
                _log.debug('start completation of group {}'.format(g.name))
                completer.complete_group(g, merged_properties, nodes_yaml,
                                         policy, constraints, interactive,
                                         df_host)
                to_complete = True
            except Exception as e:
                errors.append(' '.join(e.args))
                _log.debug(traceback.format_exc())

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
            except Exception as e:
                errors.append(' '.join(e.args))
                _log.debug(traceback.format_exc())

    if len(errors) == 0 and to_complete:
        _write_updates(tosca_yaml, new_path)
    elif len(errors) > 0:
        raise Exception(*errors)
    else:
        raise Exception('no abstract node founded')


def _validate_node_filter(tosca):
    # TODO: implement validation of the node_filter properties
    return
    raise Exception('node_filter validation error')
