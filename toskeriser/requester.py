import requests

from .exceptions import TkStackException
from .helper import CONST, Logger


def search_images(query, df_host):
    json = _request(df_host, CONST.DF_SEARCH, query)
    if 'images' in json:
        return json['count'], json['images']
    raise TkStackException('Dockerfinder server error')


def get_software(df_host):
    json = _request(df_host, CONST.DF_SOFTWARE)
    if 'software' in json:
        return [s['name'] for s in json['software']]
    raise TkStackException('Dockerfinder server error')


def _request(df_host, endpoint, params={}):
    _log = Logger.get(__name__)
    url = df_host + endpoint
    ret = requests.get(url, params=params,
                       headers={'Accept': 'applicaiton/json',
                                'Content-type': 'application/json'})
    _log.debug('request done on url {}'.format(ret.url))
    return ret.json()
