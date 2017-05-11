from sys import argv
from six import print_
from toscaparser.tosca_template import ToscaTemplate
import ruamel.yaml
import requests

# DOCKERFINDER_URL = 'http://131.114.2.77/search'
# DOCKERFINDER_URL = 'http://127.0.0.1:3000/search'
DOCKERFINDER_URL = 'http://black.di.unipi.it'
SEARCH_ENDPOINT = '/search'


def _is_abstract(node):
    if node.type == 'tosker.nodes.Container':
        if 'properties' in node.entity_tpl:
            if 'metadata' in node.entity_tpl['properties']:
                return True
    return False


def _build_query(metadata):
    errors = []

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
        # gt	/api/images?size__gt=200	Gets images with size > 200 bytes.
        # gte	/api/images?size__gte=200	Gets images with size ≥ 200 bytes.
        # lt	/api/images?size__lt=200	Gets images with size < 200 bytes.
        # lte	/api/images?size__lte=200	Gets images with size ≤ 200 bytes.
        # in	/api/images?size__in=30,200	Gets images with size 30 or 200 bytes
        # nin   /api/images?size__nin=18,30	Gets images with size not 18, 30.
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

    query = {'sort': 'stars',
             'sort': '-size',
             'sort': 'pulls',
             'size_gt': 0}
    if 'software' in metadata:
        for k, v in metadata['software'].items():
            query[k.lower()] = v
    if 'size' in metadata:
        try:
            op, num = parse_unit_limit(metadata['size'])
            query['size_{}'.format(op)] = num
        except Exception as e:
            errors.append(e.args[0])
    if 'pulls' in metadata:
        try:
            op, num = parse_limit(metadata['pulls'])
            query['pulls_{}'.format(op)] = num
        except Exception as e:
            errors.append(e.args[0])
    if 'stars' in metadata:
        try:
            op, num = parse_limit(metadata['stars'])
            query['stars_{}'.format(op)] = num
        except Exception as e:
            errors.append(e.args[0])

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
    metadata = node.entity_tpl['properties']['metadata']
    query = _build_query(metadata)
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
                                    width=10000,
                                    indent=2, block_seq_indent=2,
                                    line_break=False)


def _gen_new_path(tosca):
    return '{}/{}.completed.yaml'.format(
        '/'.join(tosca.path.split('/')[:-1]),
        tosca.input_path.split('/')[-1][:-5])


def update_tosca(file_path):
    tosca = ToscaTemplate(file_path)
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
        new_path = _gen_new_path(tosca)
        _write_updates(tosca_yaml, new_path)
    else:
        print_('ERRORS:\n{}'.format('\n'.join(errors)))


if __name__ == '__main__':
    if len(argv) < 2:
        print_('few arguments')
        exit(-1)
    update_tosca(argv[1])
