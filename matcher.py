from sys import argv
import yaml
from toscaparser.tosca_template import ToscaTemplate
import ruamel.yaml


def _is_abstract(node):
    if node.type == 'tosker.nodes.Container':
        if 'properties' in node.entity_tpl:
            if 'metadata' in node.entity_tpl['properties']:
                return True
    return False


def _build_query(metadata):
    pass


def _request(query):
    pass


def _choose_image(images):
    return 'node:6'


def _complete(node, node_yaml, tosca):
    metadata = node.entity_tpl['properties']['metadata']
    query = _build_query(metadata)
    images = _request(query)
    image = _choose_image(images)
    node_yaml['artifacts'] = {
        'my_image': {
            'file': image,
            'type': 'tosker.artifacts.Image',
            'repository': 'docker_hub'
        }
    }
    print(node_yaml)


def _write_updates(tosca, new_path):
    with open(new_path, "w") as f:
        ruamel.yaml.round_trip_dump(tosca, f,
                                    width=10000,
                                    indent=2, block_seq_indent=2,
                                    line_break=False)
        # yaml.dump(tosca.tpl, f, default_flow_style=False)


def update_tosca(file_path):
    tosca = ToscaTemplate(file_path)
    tosca_yaml = ruamel.yaml.round_trip_load(open(file_path),
                                             preserve_quotes=True)

    if hasattr(tosca, 'nodetemplates'):
        if tosca.nodetemplates:
            for node in tosca.nodetemplates:
                if _is_abstract(node):
                    node_yaml = tosca_yaml['topology_template']['node_templates'][node.name]
                    _complete(node, node_yaml, tosca)

    base_path = '/'.join(tosca.path.split('/')[:-1]) + '/'
    tosca_name = tosca.input_path.split('/')[-1][:-5]
    new_path = base_path + tosca_name + '_UP.yaml'

    _write_updates(tosca_yaml, new_path)


if __name__ == '__main__':
    if len(argv) < 2:
        print('few arguments')
        exit(-1)
    update_tosca(argv[1])
