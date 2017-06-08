import re
import os
import logging
import traceback
import sys
from sys import argv
from os import path
from six import print_
from six import StringIO
from . import __version__
from . import helper
from . import analyser
from .helper import Logger
from .helper import CONST


_USAGE = '''TosKeriser, a tool to complete TosKer application description with suitable Docker Images.

toskerise FILE [COMPONENT..] [OPTIONS]
toskerise --help|-h
toskerise --version|-v

FILE
  TOSCA YAML file or a CSAR to be completed

COMPONENT
  a list of component to be completed (by default all component are considered)

OPTIONS
  --debug                              active debug mode
  -q|--quiet                           active quiet mode
  -i|--interactive                     active interactive mode
  -f|--force                           force the update of all containers
  --constraints=value                  constraint to give to DockerFinder
                                       (e.g. --constraints 'size<=100MB pulls>30 stars>10')
  --policy=top_rated|size|most_used    ordering of the images
'''

_log = None


def run():
    global _log
    if len(argv) > 1:
        try:
            file_path, comps, flags, params = _parse_input(argv[1:])
        except Exception as e:
            print_(''.join(e.args))
            exit(-1)
    else:
        print_('few arguments, --help for usage')
        exit(-1)

    if flags.get('help', False):
        print_(_USAGE)
        exit(0)
    if flags.get('version', False):
        print_('TosKeriser version {}'.format(__version__))
        exit(0)

    Logger.set_logger(logging.CRITICAL)
    if flags.get('debug', False) and not flags.get('quiet', False):
        Logger.set_logger(logging.DEBUG)
    elif flags.get('quiet', False):
        old_target, sys.stdout = sys.stdout, StringIO()

    _log = Logger.get(__name__)
    _log.debug('input parameters: {}, {}, {}, {}'.format(
        file_path, comps, flags, params))

    constraint = params.get('constraints', {})
    _log.debug('constraints {}'.format(constraint))

    policy = params.get('policy', None)
    _log.debug('policy {}'.format(policy))

    df_host = os.environ.get('DOCKERFINDER_HOST', CONST.DF_HOST)
    _log.debug('DF_HOST: {}'.format(df_host))
    try:
        analyser.analyse_description(file_path, components=comps,
                                     policy=policy,
                                     constraints=constraint,
                                     interactive=flags.get(
                                         'interactive', False),
                                     force=flags.get('force', False),
                                     df_host=df_host)
    except Exception as e:
        _log.debug('error: {}'.format(traceback.format_exc()))
        print_(' '.join(e.args))
    finally:
        if flags.get('quiet', False):
            sys.stdout = old_target


def _parse_contraint(con):
    ret = {}
    size_re = re.compile('(?<=size)\s*(>|<|=|>=|<=)\s*[0-9]+[A-z]+')
    pulls_re = re.compile('(?<=pulls)\s*(>|<|=|>=|<=)\s*[0-9]+')
    stars_re = re.compile('(?<=stars)\s*(>|<|=|>=|<=)\s*[0-9]+')

    size = size_re.search(con)
    if size is not None:
        ret['size'] = size.group(0)

    pulls = pulls_re.search(con)
    if pulls is not None:
        ret['pulls'] = pulls.group(0)

    stars = stars_re.search(con)
    if stars is not None:
        ret['stars'] = stars.group(0)

    return ret


def _parse_policy(policy):
    if policy is not None and\
       policy not in (CONST.POLICY_TOP, CONST.POLICY_SIZE, CONST.POLICY_USED):
        raise Exception('policy must be "{0.POLICY_TOP}", '
                        '"{0.POLICY_SIZE}" or "{0.POLICY_USED}"'.format(CONST))
    else:
        return policy


_FLAG = {
    '--debug': 'debug',
    '-q': 'quiet',
    '--quiet': 'quiet',
    '--help': 'help',
    '-h': 'help',
    '-v': 'version',
    '--version': 'version',
    '-i': 'interactive',
    '--interactive': 'interactive',
    '-f': 'force',
    '--force': 'force'
}

_PARAMS = {
    '--policy': _parse_policy,
    '--constraints': _parse_contraint
}


def _parse_input(args):
    params = {}
    comps = []
    flags = {}
    file = ''
    p1 = re.compile('--.*')
    p2 = re.compile('-.??$')
    p3 = re.compile('-.*')

    def check_file(file):
        file_name = None
        if path.isfile(file):
            if file.endswith(('.yaml', '.csar', '.CSAR', '.YAML')):
                file_name = file
        return file_name

    def get_value(i):
        value = []
        old_i = i
        while i < len(args) and (not p1.match(args[i]) and
                                 not p2.match(args[i])):
            i += 1
        return ' '.join(args[old_i:i]), i

    i = 0
    while i < len(args):
        if p1.match(args[i]):
            if _FLAG.get(args[i], False):
                flags[_FLAG[args[i]]] = True
            elif args[i] in _PARAMS:
                if (i + 1 < len(args) and
                    not p1.match(args[i + 1]) and
                        not p2.match(args[i + 1])):
                    value, new_i = get_value(i + 1)
                    params[args[i][2:]] = _PARAMS[args[i]](value)
                    i = new_i
                    continue
                else:
                    raise Exception('missing input value for {}'.format(
                        args[i]))
            else:
                raise Exception('parameter {} not recognise'.format(args[i]))
        elif p2.match(args[i]):
            if _FLAG.get(args[i], False):
                flags[_FLAG[args[i]]] = True
            else:
                raise Exception('known parameter.')
        elif p3.match(args[i]):
            for c in args[i][1:]:
                c = '-{}'.format(c)
                if _FLAG.get(c, False):
                    flags[_FLAG[c]] = True
                else:
                    raise Exception('known parameter.')
        elif args[i] and file:
            comps.append(args[i])
        elif i == 0:
            file = check_file(args[i])
            if file is None:
                raise Exception('first argument must be a TOSCA yaml file, '
                                'a CSAR or a ZIP archive.')
        i += 1
    return file, comps, flags, params


if __name__ == '__main__':
    run()
