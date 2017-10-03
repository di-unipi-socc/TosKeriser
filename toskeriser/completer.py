import copy
import re

import requests
from six import print_

from . import helper
from .exceptions import TosKeriserException
from .helper import CONST, Logger

_log = None


def complete(node, nodes_yaml, tosca,
             policy=None, constraints=None, interactive=False,
             df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    properties = helper.get_host_node_filter(node)
    _log.debug('properties: {}'.format(properties))

    count, images = _get_images(properties, policy, constraints, df_host)

    if count == 0:
        raise TosKeriserException(
            'no image found for container "{}"'.format(node.name))

    print_('founded {:0} images for "{.name}" component'.format(count, node))

    image = _choose_image(images, interactive)

    _update_yaml(node, nodes_yaml, image)

    print_('complete node "{}" with image "{}" ({:.2f} MB, {} pulls, {} stars)'
           ''.format(node.name, image['name'],
                     image['size'] / 1000000, image['pulls'], image['stars']))


def complete_group(group, properties, nodes_yaml,
                   policy=None, constraints=None, interactive=False,
                   df_host=CONST.DF_HOST):

    count, images = _get_images(properties, policy, constraints, df_host)

    if count == 0:
        raise TosKeriserException(
            'no image found for group "{}"'.format(group.name))

    print_('founded {} images for group "{}" component'
           ''.format(count, group.name))

    image = _choose_image(images, interactive)

    _update_group_yaml(group, properties, nodes_yaml, image)

    print_('complete group "{}" with image "{}" '
           '({:.2f} MB, {} pulls, {} stars)'
           ''.format(group.name, image['name'], image['size'] / 1000000,
                     image['pulls'], image['stars']))


def _get_images(properties,
                policy=None, constraints=None, df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    query = _build_query(properties, policy, constraints)
    _log.debug('query {}'.format(query))

    responce = _request(query, df_host)
    images = responce['images']
    _log.debug('returned images..')

    if len(images) < 1:
        return 0, None
    return responce['count'], images


def _build_query(properties, policy=None, constraints={}):
    policy = CONST.POLICY_TOP if policy is None else policy
    errors = []

    def parse_functions(f):
        _log.debug(f)
        if not isinstance(f, dict):
            return f
        else:
            (op, value), = f.items()
            if 'equal' == op:
                return value
            elif op in ('greater_or_equal', 'greater_than',
                        'less_than', 'less_or_equal'):
                raise TosKeriserException(
                    'in parsing {}: function not supported'
                    ''.format(f))
            else:
                raise TosKeriserException(
                    'in parsing {}: function not recognise'
                    ''.format(f))

    def parse_version(s):
        s = parse_functions(str(s))
        match = re.match('^([0-9]+.)*([0-9]+|x)?$', s)
        if match is not None:
            version = re.match('[0-9]+(\\.[0-9]+)*', s)
            return version.group(0) if version is not None else ''
        else:
            raise TosKeriserException(
                'in parsing {}: version format is not correct'
                ''.format(s))

    def parse_unit(s):
        # bytes -> bytes
        # kB    -> kilo bytes
        # MB    -> mega bytes
        # GB    -> giga bytes
        s = s.lower()
        if s.endswith('bytes'):
            return int(s[:-5])
        elif s.endswith('kb'):
            return int(s[:-2]) * 1000
        elif s.endswith('mb'):
            return int(s[:-2]) * 1000 * 1000
        elif s.endswith('gb'):
            return int(s[:-2]) * 1000 * 1000 * 1000
        else:
            raise TosKeriserException(
                'in parsing {}: unit not recognise'.format(s))

    def parse_op(s):
        if s.startswith('>='):
            return 'gte', s[2:]
        elif s.startswith('>'):
            return 'gt', s[1:]
        elif s.startswith('<='):
            return 'lte', s[2:]
        elif s.startswith('<'):
            return 'lt', s[1:]
        else:
            raise TosKeriserException(
                'in parsing {}: operator not recognise'.format(s))

    def parse_unit_limit(s):
        s = s.strip()
        op, rest = parse_op(s)
        num = parse_unit(rest)
        return op, num

    def parse_limit(s):
        s = s.strip()
        op, rest = parse_op(s)
        return op, int(rest)

    query = {'size_gt': 0}
    if CONST.POLICY_TOP == policy:
        query['sort'] = ('stars', 'pulls', '-size')
    if CONST.POLICY_SIZE == policy:
        query['sort'] = ('-size', 'stars', 'pulls')
    if CONST.POLICY_USED == policy:
        query['sort'] = ('pulls', 'stars', '-size')

    _log.debug('properties {}'.format(properties))
    for p in properties:
        if CONST.PROPERTY_SW in p:
            for s in p[CONST.PROPERTY_SW]:
                (k, v), = s.items()
                try:
                    query[k.lower()] = parse_version(v)
                except TosKeriserException as e:
                    errors += e.stack
        if CONST.PROPERTY_OS in p:
            try:
                query['distro'] = parse_functions(p[CONST.PROPERTY_OS])
            except TosKeriserException as e:
                errors += e.stack

    if 'size' in constraints:
        try:
            _log.debug('size {}'.format(constraints['size']))
            op, num = parse_unit_limit(constraints['size'])
            query['size_{}'.format(op)] = num
        except TosKeriserException as e:
            errors += e.stack
    if 'pulls' in constraints:
        try:
            op, num = parse_limit(constraints['pulls'])
            query['pulls_{}'.format(op)] = num
        except TosKeriserException as e:
            errors += e.stack
    if 'stars' in constraints:
        try:
            op, num = parse_limit(constraints['stars'])
            query['stars_{}'.format(op)] = num
        except TosKeriserException as e:
            errors += e.stack

    if len(errors) > 0:
        raise TosKeriserException(*errors)

    return query


def _request(query, df_host):
    url = df_host + CONST.DF_SEARCH
    _log.debug('prepare request on endpoint {}'.format(url))
    ret = requests.get(url, params=query,
                       headers={'Accept': 'applicaiton/json',
                                'Content-type': 'application/json'})

    _log.debug('request done on url {}'.format(ret.url))
    json = ret.json()
    if 'images' in json:
        return json
    raise TosKeriserException('Dockerfinder server error')


def _choose_image(images, interactive=False):
    def format_size(size):
        return '{}MB'.format(size / 1000 / 1000)

    if interactive:
        # print_('\n')
        print_('{:<3}{:<30}{:>15}{:>15}{:>15}'.format(
               '#', 'NAME', 'SIZE', 'PULLS', 'STARS'))
        for index, image in enumerate(images[:10]):
            print_('{2:<3}{0[name]:<30}{1:>15}'
                   '{0[pulls]:>15}{0[stars]:>15}'.format(
                       image, format_size(image['size']), index + 1))
        # print_('\n')
        i = None
        while not isinstance(i, int):
            try:
                i = int(input('select an image number ')) - 1
                if i < 0 or i > len(images) - 1:
                    _log.debug('not in range')
                    raise Exception()
                return images[i]
            except Exception as e:
                i = None
                print_('must be a number between 1 and {}'.format(len(images)))
    else:
        return images[0] if len(images) > 0 else None


def _update_yaml(node, nodes_yaml, image):
    # update host requirement of all node of the group
    container_name = '{}_container'.format(node.name)
    req_node_yaml = helper.get_host_requirements(nodes_yaml[node.name])
    req_node_yaml['node'] = container_name

    # add container node to the template
    try:
        prop = req_node_yaml['node_filter']['properties']
    except (KeyError, TypeError):
        prop = []
    nodes_yaml[container_name] = _build_container_node(image, prop)


def _update_group_yaml(group, node_filter, nodes_yaml, image):
    # update host requirement of all node of the group
    container_name = '{}_container'.format(group.name)
    for m in group.members:
        req_node_yaml = helper.get_host_requirements(nodes_yaml[m.name])
        req_node_yaml['node'] = container_name

    # add container node to the template
    nodes_yaml[container_name] = _build_container_node(image, node_filter)


def _build_container_node(image, node_filter):
    def node_filter_to_property(node_filter):
        def list_to_map(l):
            return {k: v for i in l for k, v in i.items()}

        new_prop = {k: copy.deepcopy(list_to_map(v)
                                     if isinstance(v, list) else v)
                    for p in node_filter for k, v in p.items()
                    if CONST.PROPERTY_SW != k and CONST.PROPERTY_OS != k}
        return new_prop

    new_prop = node_filter_to_property(node_filter)\
        if node_filter is not None else {}

    def format_software(softwares):
        return {s['software']: s['ver'] for s in softwares}

    properties = {}
    if 'softwares' in image and len(image['softwares']) > 0:
        properties[CONST.PROPERTY_SW] = format_software(image['softwares'])
    if 'distro' in image and image['distro']:
        properties[CONST.PROPERTY_OS] = image['distro']

    properties.update(new_prop)

    return {
        'type': 'tosker.nodes.Container',
        'properties': properties,
        'artifacts': {
            'my_image': {
                'file': image['name'],
                'type': 'tosker.artifacts.Image',
                'repository': 'docker_hub'
            }
        }
    }
