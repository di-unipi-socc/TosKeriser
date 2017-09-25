from .helper import Logger

_log = None


def merge(nodes_property):
    global _log
    _log = Logger.get(__name__)

    for n in nodes_property:
        for p in n:
            key, value = list(p.items())[0]
            _log.debug('k:{} v:{}'.format(key, value))

            if 'os_distribution' == key:
                pass
