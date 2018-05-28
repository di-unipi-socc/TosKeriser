import requests

from .exceptions import TkException
from .helper import CONST, Logger


def search_images(query, df_host):
    try:
        json = _request(df_host, CONST.DF_SEARCH, query)
        return json['count'], json['images']
    except (TkException, KeyError):
        raise TkException('Dockerfinder server error')


def get_software(df_host):
    try:
        json = _request(df_host, CONST.DF_SOFTWARE)
        return [s['name'] for s in json['software']]
    except (TkException, KeyError):
        raise TkException('Dockerfinder software service do not respond')


def _request(df_host, endpoint, params={}):
    _log = Logger.get(__name__)
    url = df_host + endpoint
    try:
        ret = requests.get(url, params=params,
                           headers={'Accept': 'applicaiton/json',
                                    'Content-type': 'application/json'},
                           timeout=5)
        _log.debug('request done on url {}'.format(ret.url))
    except requests.exceptions.RequestException as e:
        _log.debug('Request error: %s', e)
        raise TkException('Request to Dockerfinder fails.')
    return ret.json()
