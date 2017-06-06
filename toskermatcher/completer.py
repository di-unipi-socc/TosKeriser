import requests
from six import string_types
from six import print_
from . import helper
from .helper import Logger
from .helper import CONST

_log = None


def _build_query(properties, policy=None, constraints={}):
    policy = CONST.POLICY_TOP if policy is None else policy
    errors = []

    def parse_functions(f):
        _log.debug(f)
        if f is None:
            return ''
        elif not isinstance(f, dict):
            return f
        else:
            # TODO: implement functions
            (op, value), = f.items()
            if 'equal' == op:
                return value
            elif 'greater_or_equal' == op:
                return value
            elif 'greater_than' == op:
                return value
            elif 'less_than' == op:
                return value
            elif 'less_or_equal' == op:
                return value
            else:
                raise Exception('in parsing {}: function not recognise'
                                ''.format(f))

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
            raise Exception('in parsing {}: unit not recognise'.format(s))

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
            raise Exception('in parsing {}: operator not recognise'.format(s))

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
                    query[k.lower()] = parse_functions(v)
                except Exception as e:
                    errors.append(e.args[0])
        if CONST.PROPERTY_OS in p:
            try:
                query['distro'] = parse_functions(p[CONST.PROPERTY_OS])
            except Exception as e:
                errors.append(e.args[0])

    if 'size' in constraints:
        try:
            _log.debug('size {}'.format(constraints['size']))
            op, num = parse_unit_limit(constraints['size'])
            query['size_{}'.format(op)] = num
        except Exception as e:
            errors.append(e.args[0])
    if 'pulls' in constraints:
        try:
            op, num = parse_limit(constraints['pulls'])
            query['pulls_{}'.format(op)] = num
        except Exception as e:
            errors.append(e.args[0])
    if 'stars' in constraints:
        try:
            op, num = parse_limit(constraints['stars'])
            query['stars_{}'.format(op)] = num
        except Exception as e:
            errors.append(e.args[0])

    if len(errors) > 0:
        raise Exception('\n'.join(errors))

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
    raise Exception('Dockerfinder server error')


def _choose_image(images, interactive=False):
    def format_size(size):
        return '{}MB'.format(size/1000/1000)

    if interactive:
        # print_('\n')
        print_('{:<3}{:<30}{:>15}{:>15}{:>15}'.format(
               '#', 'NAME', 'SIZE', 'PULLS', 'STARS'))
        for index, image in enumerate(images[:10]):
            print_('{2:<3}{0[name]:<30}{1:>15}'
                   '{0[pulls]:>15}{0[stars]:>15}'.format(
                    image, format_size(image['size']), index+1))
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
    def format_software(image):
        res = {}
        for s in image['softwares']:
            res[s['software']] = s['ver']
        return res

    container_name = '{}_container'.format(node.name)
    req_node_yaml = helper.get_host_requirements(nodes_yaml[node.name])
    req_node_yaml['node'] = container_name

    nodes_yaml[container_name] = {
        'type': 'tosker.nodes.Container',
        'properties': {
            CONST.PROPERTY_SW: format_software(image),
            CONST.PROPERTY_OS: image['distro']
        },
        'artifacts': {
            'my_image': {
                'file': image['name'],
                'type': 'tosker.artifacts.Image',
                'repository': 'docker_hub'
            }
        }
    }


def complete(node, nodes_yaml, tosca,
             policy=None, constraints=None, interactive=False,
             df_host=CONST.DF_HOST):
    global _log
    _log = Logger.get(__name__)
    requirement = helper.get_host_requirements(node)
    properties = requirement['node_filter']['properties']

    query = _build_query(properties, policy, constraints)
    _log.debug('query {}'.format(query))

    responce = _request(query, df_host)
    images = responce['images']
    _log.debug('returned images..')

    if len(images) < 1:
        raise Exception('no image found for container "{}"'.format(node.name))

    print_('founded {[count]} images for "{.name}"'
           ' component'.format(responce, node))

    image = _choose_image(images, interactive)

    _update_yaml(node, nodes_yaml, image)

    print_('complete node "{}" with image "{}" ({:.2f} MB, {} pulls, {} stars)'
           ''.format(node.name, image['name'],
                     image['size'] / 1000000, image['pulls'], image['stars']))
