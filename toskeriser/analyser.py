import ruamel.yaml
import traceback
from os import path
from six import print_
from six import string_types
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.common.exception import ValidationError
from . import helper
from . import completer
from .helper import Logger
from .helper import CONST

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
        print_('validation error:{}'.format(e))
    except Exception as e:
        _log.error('error type {}'.format(type(e)))
        print_(', '.join(e.args))


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

def _must_update(node, force):
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

    if is_software(node) and \
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

    tosca = ToscaTemplate(file_path)
    _log.debug('tosca: {}'.format(tosca))

    path_name = path.dirname(file_path)
    name = tosca.input_path.split('/')[-1][:-5]

    _check_components(tosca, components)

    tosca_yaml = ruamel.yaml.round_trip_load(open(file_path),
                                             preserve_quotes=True)
    errors = []
    to_complete = False
    if hasattr(tosca, 'nodetemplates'):
        if tosca.nodetemplates:
            for node in tosca.nodetemplates:
                nodes_yaml = tosca_yaml['topology_template']['node_templates']
                if len(components) == 0 or node.name in components:
                    if _must_update(node, force):
                        to_complete = True
                        _log.debug('node {.name} is abstract'.format(node))
                        try:
                            completer.complete(node, nodes_yaml, tosca,
                                               policy, constraints,
                                               interactive, df_host)
                        except Exception as e:
                            _log.error('error: {}'.format(
                                traceback.format_exc()))
                            errors.append(' '.join(e.args))

    if len(errors) == 0 and to_complete:
        _write_updates(tosca_yaml, new_path)
    elif len(errors) > 0:
        raise Exception('ERRORS:\n{}'.format('\n'.join(errors)))
    else:
        raise Exception('no abstract node founded')
