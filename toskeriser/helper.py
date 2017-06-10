import os
import zipfile
import logging
from os import path
from toscaparser.prereq.csar import CSAR
from toscaparser.common.exception import ValidationError


class CONST:
    # DF_HOST = 'http://131.114.2.77/search'
    # DF_HOST = 'http://127.0.0.1:3000/search'
    DF_HOST = 'http://black.di.unipi.it:3000'
    DF_SEARCH = '/search'

    # CONTAINER_TYPE = 'tosker.nodes.Container'
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


def get_host_requirements(node):
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
