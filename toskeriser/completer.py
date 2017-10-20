import copy
import re

from six import print_

from . import helper, requester
from .exceptions import TkStackException
from .helper import CONST, Group, Logger

_log = None


def complete(component, nodes_yaml, tosca,
             policy=None, constraints=None, interactive=False,
             df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)

    properties = component.constraints
    _log.debug('properties: {}'.format(properties))

    count, images = _get_images(properties, policy, constraints, df_host)

    print_('founded {:0} images for "{.name}" node'
           ''.format(count, component))

    if count == 0:
        print_('[WARNING] node "{.name}" will not be completed'
               ''.format(component))
        return False

    image = _choose_image(images, interactive)

    if isinstance(component, Group):
        _update_group_yaml(component, nodes_yaml, image)
        print_('complete group "{}" with image "{}" '
               '({:.2f} MB, {} pulls, {} stars)'
               ''.format(component.name, image['name'],
                         image['size'] / 1000000, image['pulls'],
                         image['stars']))
    else:
        _update_yaml(component, nodes_yaml, image)
        print_('complete node "{}" with image "{}" '
               '({:.2f} MB, {} pulls, {} stars)'
               ''.format(component.name, image['name'],
                         image['size'] / 1000000, image['pulls'],
                         image['stars']))
    return True


def _get_images(properties, policy=None, constraints=None,
                df_host=CONST.DF_HOST):
    query = _build_query(properties, policy, constraints)
    _log.debug('query {}'.format(query))

    count, images = requester.search_images(query, df_host)
    _log.debug('returned images..')

    if len(images) < 1:
        return 0, None
    return count, images


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
                raise TkStackException(
                    'in parsing {}: function not supported'
                    ''.format(f))
            else:
                raise TkStackException(
                    'in parsing {}: function not recognise'
                    ''.format(f))

    def parse_version(s):
        s = parse_functions(str(s))
        match = re.match('^([0-9]+.)*([0-9]+|x)$', s)
        if match is not None:
            version = re.match('[0-9]+(.[0-9]+)*', s)
            return version.group(0) if version is not None else ''
        else:
            raise TkStackException(
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
            raise TkStackException(
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
            raise TkStackException(
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
                except TkStackException as e:
                    errors += e.stack
        if CONST.PROPERTY_OS in p:
            try:
                query['distro'] = parse_functions(p[CONST.PROPERTY_OS])
            except TkStackException as e:
                errors += e.stack

    if 'size' in constraints:
        try:
            _log.debug('size {}'.format(constraints['size']))
            op, num = parse_unit_limit(constraints['size'])
            query['size_{}'.format(op)] = num
        except TkStackException as e:
            errors += e.stack
    if 'pulls' in constraints:
        try:
            op, num = parse_limit(constraints['pulls'])
            query['pulls_{}'.format(op)] = num
        except TkStackException as e:
            errors += e.stack
    if 'stars' in constraints:
        try:
            op, num = parse_limit(constraints['stars'])
            query['stars_{}'.format(op)] = num
        except TkStackException as e:
            errors += e.stack

    if len(errors) > 0:
        raise TkStackException(*errors)

    return query


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
    node_yaml = nodes_yaml[node.name]
    # req_node_yaml = helper.get_host(node_yaml)
    # _log.debug('req_node_yaml {}, type {}'
    #            ''.format(req_node_yaml, type(req_node_yaml)))
    node_host = helper.get_host_node(node_yaml)
    if node_host != container_name:
        _log.debug('there is a different container')
        del nodes_yaml[node_host]
    helper.set_host_node(node_yaml, container_name)

    nodes_yaml[container_name] = _build_container_node(image, node.constraints)


def _update_group_yaml(component, nodes_yaml, image):
    # update host requirement of all node of the group
    container_name = '{}_container'.format(component.name)
    for m in (m for m in component.members if m.to_update):
        node_host = helper.get_host_node(m)
        if node_host != container_name:
            _log.debug('there is a different container')
            del nodes_yaml[node_host]
        helper.set_host_node(nodes_yaml[m.name], container_name)

    # add container node to the template
    node_filter = component.constraints
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
