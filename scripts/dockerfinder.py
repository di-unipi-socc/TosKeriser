import json
import logging
from sys import argv

from six import print_
from tabulate import tabulate

from toskeriser import requester
from toskeriser.helper import Logger

if len(argv) < 2:
    exit(-1)

params = {"size_gt": 0, "pulls_gt": 0, "stars_gt": 0, "page": 1}

for sw in argv[1].split(','):
    if '=' in sw:
        s, v = sw.split('=')
        params[s] = v
    else:
        params[sw] = ''

params['sort'] = argv[2].split(',') if len(argv) > 2 else ('stars', 'pulls', '-size')

print_('DEBUG', params)
Logger.set_logger(logging.DEBUG)
count, images = requester.search_images(params, 'http://black.di.unipi.it')

print_('#images', count)
table = tabulate(
    [[i['name'], i['size']/1000/1000, i['pulls'], i['stars']
    #  ','.join(['{}:{}'.format(s['software'], s['ver']) for s in i['softwares']])
    ] for i in images[:10]],
    headers=['Name', 'Size (MB)', 'Pulls', 'Stars'])
print_(table)
try:
    selection = int(input('image: '))
    print_(json.dumps(images[selection + 1], sort_keys=True, indent=2))
except ValueError:
    exit()
