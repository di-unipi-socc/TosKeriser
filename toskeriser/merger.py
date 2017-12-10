from .exceptions import TkStackException
from .helper import CONST, Logger

_log = None


def merge_constraint(nodes_property):
    global _log
    _log = Logger.get(__name__)

    merged_properties = {}
    errors = []
    for n in nodes_property:
        for p in n:
            key, value = list(p.items())[0]
            _log.debug('k:{} v:{}'.format(key, value))

            try:
                if CONST.PROPERTY_SW == key:
                    _add_property(merged_properties, p, f_merge=_merge_version)
                else:
                    # if CONST.PROPERTY_SW of other properties
                    _add_property(merged_properties, p)
            except TkStackException as e:
                errors += e.stack

    if len(errors) != 0:
        raise TkStackException(*errors)
    _log.debug(merged_properties)
    p_list = _convert_to_list(merged_properties)
    _log.debug(p_list)
    return p_list


def _add_property(merged_p, new_p, f_merge=lambda x, y: x if x == y else None):
    '''
    Add a property to a dictionary of properties executing the f_merge to
    resolve conflicts.
    '''
    new_p_key, new_p_value = list(new_p.items())[0]

    errors = []
    # if the property to merge is a list
    if isinstance(new_p_value, list):
        if new_p_key not in merged_p:
            merged_p[new_p_key] = {}

        for p in new_p_value:
            p_name, p_value = list(p.items())[0]

            if p_name not in merged_p[new_p_key]:
                merged_p[new_p_key][p_name] = p_value
            else:
                res = f_merge(merged_p[new_p_key][p_name], p_value)
                if res is not None:
                    merged_p[new_p_key][p_name] = res
                else:
                    errors.append('Cannot merge value "{}" with "{}" of '
                                  'property "{}"'
                                  ''.format(
                                      merged_p[new_p_key][p_name],
                                      p_value, new_p_key + '.' + str(p_name)))

    # if the property to merge is a string
    else:
        if new_p_key not in merged_p:
            merged_p[new_p_key] = new_p_value
        else:
            res = f_merge(merged_p[new_p_key], new_p_value)
            if res is not None:
                merged_p[new_p_key] = res
            else:
                errors.append('Cannot merge value "{}" with "{}" of '
                              'property "{}"'
                              ''.format(merged_p[new_p_key], new_p_value,
                                        new_p_key))

    if len(errors) != 0:
        raise TkStackException(*errors)


def _merge_version(v1, v2):
    '''
    Merge two software version. It return the merged one or None
    if the merge is not possible
    '''
    v1 = v1.split('.')
    v2 = v2.split('.')
    min_len = len(v1) if len(v1) < len(v2) else len(v2)

    merged_version = []
    i = 0
    while i < min_len and v1[i] != 'x' and v2[i] != 'x':
        if v1[i] == v2[i]:
            merged_version.append(v1[i])
        else:
            return None
        i += 1

    if i < len(v1) and v1[i] == 'x':
        return '.'.join(merged_version + v2[i:])
    elif i < len(v2) and v2[i] == 'x':
        return '.'.join(merged_version + v1[i:])
    elif len(v1) != len(v2):
        return None
    else:
        return '.'.join(merged_version)


def _convert_to_list(properties):
    if isinstance(properties, dict) and 'get_input' not in properties.keys():
        return [{k: _convert_to_list(v)} for k, v in properties.items()]
    else:
        return properties
