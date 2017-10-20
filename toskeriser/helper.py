import logging
import os
import zipfile
from os import path

from six import string_types
from toscaparser.prereq.csar import CSAR


class CONST:
    # DF_HOST = 'http://131.114.2.77/search'
    # DF_HOST = 'http://127.0.0.1:3000/search'
    DF_HOST = 'http://black.di.unipi.it'
    DF_SEARCH = ':3000/search'
    DF_SOFTWARE = ':3001/api/software'

    CONTAINER_TYPE = 'tosker.nodes.Container'
    SOFTWARE_TYPE = 'tosker.nodes.Software'
    # IMAGE_TYPE = 'tosker.artifacts.Image'
    # DOCKERFILE_TYPE = 'tosker.artifacts.Dockerfile'

    PROPERTY_SW = 'supported_sw'
    PROPERTY_OS = 'os_distribution'
    REQUIREMENT_HOST = 'host'

    POLICY_TOP = 'top_rated'
    POLICY_SIZE = 'size'
    POLICY_USED = 'most_used'


class Logger:
    _ch = None

    @staticmethod
    def set_logger(level=logging.DEBUG):
        # global Logger._ch
        Logger._ch = logging.StreamHandler()
        Logger._ch.setLevel(level)
        formatter = logging.Formatter((
            '%(levelname) -3s %(asctime)s %(name)'
            '-3s %(funcName)'
            '-1s %(lineno) -0s: %(message)s'
        ))
        Logger._ch.setFormatter(formatter)

    @staticmethod
    def get(name, level=logging.DEBUG):
        log = logging.getLogger(name)
        log.setLevel(level)
        if Logger._ch is not None:
            log.addHandler(Logger._ch)
        return log


class Group:

    def __init__(self, name, members):
        self.name = name
        self.members = members


def unpack_csar(file_path):
    # Work around bug validation csar of toscaparser
    csar = CSAR(file_path)
    try:
        csar.validate()
    except ValueError as e:
        # _log.debug(e)
        if not str(e).startswith("The resource") or \
           not str(e).endswith("does not exist."):
            raise e

    csar.decompress()

    yaml_path = path.join(csar.temp_dir, csar.get_main_template())
    return (csar.temp_dir, yaml_path)


def pack_csar(csar_tmp_path, new_path):
    with zipfile.ZipFile(new_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirname, subdirs, files in os.walk(csar_tmp_path):
            # zf.write(dirname, root)
            for filename in files:
                zf.write(path.join(dirname, filename),
                         path.relpath(path.join(dirname, filename),
                                      path.join(csar_tmp_path, '.')))


def convert_tosca_group(tosca):
    return [Group(g.name,
                  [get_node_from_tpl(tosca, m) for m in g.members])
            for g in tosca.topology_template.groups]


def get_host(node):
    if hasattr(node, 'entity_tpl'):
        node = node.entity_tpl
    if 'requirements' in node:
        for r in node['requirements']:
            (k, v), = r.items()
            if CONST.REQUIREMENT_HOST == k:
                if v is None:
                    r[k] = {}
                return r[k]
    return None


def get_host_key(node, key):
    requirement = get_host(node)
    if requirement is not None and isinstance(requirement, dict):
        if key in requirement:
            return requirement[key]
    return None


def set_host_node(node, host_node):
    if 'requirements' in node:
        for r in node['requirements']:
            (k, v), = r.items()
            if CONST.REQUIREMENT_HOST == k:
                if not isinstance(v, dict):
                    r[k] = host_node
                else:
                    r[k]['node'] = host_node
                return True
    return False


def get_host_node(node):
    requirement = get_host(node)
    if isinstance(requirement, string_types):
        return requirement
    return get_host_key(node, 'node')


def get_host_nodefilter(node):
    requirement = get_host(node)
    try:
        properties = requirement['node_filter']['properties'] or []
    except (TypeError,  KeyError):
        properties = []
    return properties


def get_node_from_tpl(tosca, str_node):
    for node in tosca.nodetemplates:
        if node.name == str_node:
            return node
    return None
