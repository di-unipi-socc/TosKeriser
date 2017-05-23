import ruamel.yaml
import requests
import re
import shutil
import os
import zipfile
from sys import argv
from os import path
from six import print_
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.prereq.csar import CSAR
from toscaparser.common.exception import ValidationError

# DOCKERFINDER_URL = 'http://131.114.2.77/search'
# DOCKERFINDER_URL = 'http://127.0.0.1:3000/search'
DOCKERFINDER_URL = 'http://black.di.unipi.it:3000'
SEARCH_ENDPOINT = '/search'

PROPERTY_SW = 'installed_sw'
PROPERTY_OS = 'os_distribution'


def _is_abstract(node):
    if node.type == 'tosker.nodes.Container':
        if 'properties' in node.entity_tpl:
            if PROPERTY_OS in node.entity_tpl['properties'] or\
               PROPERTY_SW in node.entity_tpl['properties']:
                return True
    return False


def _build_query(properties):
    errors = []

    # def parse_unit(s):
    #     # bytes -> bytes
    #     # kB    -> kilo bytes
    #     # MB    -> mega bytes
    #     # GB    -> giga bytes
    #     s = s.lower()
    #     if s.endswith('bytes'):
    #         return int(s[:-5])
    #     elif s.endswith('kb'):
    #         return int(s[:-2]) * 1000
    #     elif s.endswith('mb'):
    #         return int(s[:-2]) * 1000 * 1000
    #     elif s.endswith('gb'):
    #         return int(s[:-2]) * 1000 * 1000 * 1000
    #     else:
    #         raise Exception('in parsing {}: unit not recognise'.format(s))
    #
    # def parse_op(s):
    #     # gt	/api/images?size__gt=200	Gets images with size > 200 bytes.
    #     # gte	/api/images?size__gte=200	Gets images with size ≥ 200 bytes.
    #     # lt	/api/images?size__lt=200	Gets images with size < 200 bytes.
    #     # lte	/api/images?size__lte=200	Gets images with size ≤ 200 bytes.
    #     # in	/api/images?size__in=30,200	Gets images with size 30 or 200 bytes
    #     # nin   /api/images?size__nin=18,30	Gets images with size not 18, 30.
    #     if s.startswith('>='):
    #         return 'gte', s[2:]
    #     elif s.startswith('>'):
    #         return 'gt', s[1:]
    #     elif s.startswith('<='):
    #         return 'lte', s[2:]
    #     elif s.startswith('<'):
    #         return 'lt', s[1:]
    #     else:
    #         raise Exception('in parsing {}: operator not recognise'.format(s))
    #
    # def parse_unit_limit(s):
    #     s = s.strip()
    #     op, rest = parse_op(s)
    #     num = parse_unit(rest)
    #     return op, num
    #
    # def parse_limit(s):
    #     s = s.strip()
    #     op, rest = parse_op(s)
    #     return op, int(rest)

    query = {'sort': ('stars', '-size', 'pulls')}
    if PROPERTY_SW in properties:
        for k, v in properties[PROPERTY_SW].items():
            query[k.lower()] = v
    if PROPERTY_OS in properties:
        # TODO: implement distribution query
        pass
    # if 'size' in properties:
    #     try:
    #         op, num = parse_unit_limit(properties['size'])
    #         query['size_{}'.format(op)] = num
    #     except Exception as e:
    #         errors.append(e.args[0])
    # if 'pulls' in properties:
    #     try:
    #         op, num = parse_limit(properties['pulls'])
    #         query['pulls_{}'.format(op)] = num
    #     except Exception as e:
    #         errors.append(e.args[0])
    # if 'stars' in properties:
    #     try:
    #         op, num = parse_limit(properties['stars'])
    #         query['stars_{}'.format(op)] = num
    #     except Exception as e:
    #         errors.append(e.args[0])

    if len(errors) > 0:
        raise Exception('\n'.join(errors))

    return query


def _request(query):
    url = DOCKERFINDER_URL + SEARCH_ENDPOINT
    ret = requests.get(url, params=query,
                       headers={'Accept': 'applicaiton/json',
                                'Content-type': 'application/json'})
    print_('DEBUG', 'url:', ret.url)
    return ret.json()['images']


def _choose_image(images):
    return images[0] if len(images) > 0 else None


def _complete(node, node_yaml, tosca):
    properties = node.entity_tpl['properties']
    query = _build_query(properties)
    images = _request(query)
    image = _choose_image(images)
    if image is None:
        raise Exception('no image found for container "{}"'.format(node.name))
    node_yaml['artifacts'] = {
        'my_image': {
            'file': image['name'],
            'type': 'tosker.artifacts.Image',
            'repository': 'docker_hub'
        }
    }
    print_('complete node "{}" with image "{}" ({:.2f} MB, {} pulls, {} stars)'
           ''.format(node.name, image['name'],
                     image['size'] / 1000000, image['pulls'], image['stars']))


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
    return '{}.{}.{}'.format(''.join(points[:-1]), mod, points[-1])


def _update_tosca(file_path, new_path):

    tosca = ToscaTemplate(file_path)
    path_name = path.dirname(file_path)
    name = tosca.input_path.split('/')[-1][:-5]

    tosca_yaml = ruamel.yaml.round_trip_load(open(file_path),
                                             preserve_quotes=True)

    errors = []
    if hasattr(tosca, 'nodetemplates'):
        if tosca.nodetemplates:
            for node in tosca.nodetemplates:
                if _is_abstract(node):
                    node_yaml = tosca_yaml['topology_template'][
                        'node_templates'][node.name]
                    try:
                        _complete(node, node_yaml, tosca)
                    except Exception as e:
                        errors.append(e.args[0])

    if len(errors) == 0:
        _write_updates(tosca_yaml, new_path)
    else:
        print_('ERRORS:\n{}'.format('\n'.join(errors)))


def run():
    if len(argv) < 2:
        print_('few arguments')
        exit(-1)

    file_path = argv[1]

    if file_path.endswith(('.zip', '.csar')):
        csar_tmp_path, yaml_path = _unpack_csar(file_path)
        _update_tosca(yaml_path, yaml_path)
        new_path = _gen_new_path(file_path, 'completed')
        _pack_csar(csar_tmp_path, new_path)
    else:
        new_path = _gen_new_path(file_path, 'completed')
        _update_tosca(file_path, new_path)


def _unpack_csar(file_path):
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


def _pack_csar(csar_tmp_path, new_path):
    _create_csar(csar_tmp_path, new_path)


def _create_csar(csar_tmp_path, path_to_save):
    # with ZipFile(path_to_save, 'w') as zp:
    #     zp.write(csar_tmp_path)
    # shutil.make_archive(path_to_save, 'zip', csar_tmp_path)

    with zipfile.ZipFile(path_to_save, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirname, subdirs, files in os.walk(csar_tmp_path):
            # zf.write(dirname, root)
            for filename in files:
                zf.write(path.join(dirname, filename),
                         path.relpath(path.join(dirname, filename),
                                      os.path.join(csar_tmp_path, '.')))


if __name__ == '__main__':
    run()
