from .helper import Logger

_log = None


def merge(nodes_property):
    # TODO: validate node_filter before merge
    global _log
    _log = Logger.get(__name__)

    merged_properties = {}

    for n in nodes_property:
        for p in n:
            key, value = list(p.items())[0]
            _log.debug('k:{} v:{}'.format(key, value))

            if 'os_distribution' == key:
                _add_property(merged_properties, p)
            elif 'supported_sw' == key:
                _add_property(merged_properties, p, f_merge=_merge_version)
            else:
                _add_property(merged_properties, p)

    _log.debug(merged_properties)
    p_list = _convert_to_list(merged_properties)
    _log.debug(p_list)
    return p_list


def _convert_to_list(properties):
    if isinstance(properties, dict):
        return [{k: _convert_to_list(v)} for k, v in properties.items()]
    else:
        return properties


def _add_property(merged_p, new_p, f_merge=lambda x, y: x if x == y else None):
    '''
    Add a property to a dictionary of properties executing the f_merge to
    resolve conflicts.
    '''
    new_p_key, new_p_value = list(new_p.items())[0]

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
                    raise Exception('Cannot merge properties')
    # if the property to merge is a string
    else:
        if new_p_key not in merged_p:
            merged_p[new_p_key] = new_p_value
        else:
            res = f_merge(merged_p[new_p_key][p_name], p_value)
            if res is not None:
                merged_p[new_p_key][p_name] = res
            else:
                raise Exception('Cannot merge properties')


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

    # for i, n in enumerate(v_longer):
    #     if i >= len(v_smaller):
    #         if n == v_smaller[i]:
    #             merged_version.append(n)
    #         else:
    #             if n == 'x':
    #                 merged_version + (v_smaller[i])
    #             elif v_smaller[i] == 'x'
    #                 merged_version.append(v_smaller[i])
    # return '.'.join(merged_version)
