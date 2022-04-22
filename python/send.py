#! /usr/bin/env python3
# Send files to Monto.

import getopt
import os
import re
import sys

from montolib import MontoSource


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'c:hs:',
                                   ['chnglang', 'help', 'selection'])
    except getopt.GetoptError as err:
        error(err)
        sys.exit(1)
    chnglang = None
    selections = []
    for o, a in opts:
        if o in ('-c', '--chnglang'):
            chnglang = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif o in ('-s', '--selection'):
            selections.append(selargtoobj(a))
        else:
            assert False, 'unhandled option'
    send(args, chnglang, selections)


def error(msg):
    print('send: {0!s}'.format(msg))
    usage()


def usage():
    print('usage: send [-c chnglang] [-s begin:end] file...')


def selargtoobj(selarg):
    m = re.match(r'^(\d+):(\d+)$', selarg)
    if m:
        begin = int(m.group(1))
        end = int(m.group(2))
        if begin <= end:
            return {'begin': begin, 'end': end}
        else:
            error('in selection \'{0}\', begin > end'.format(selarg))
            sys.exit(3)
    else:
        error('selection \'{0}\' is not of the form begin:end'.format(selarg))
        sys.exit(4)

# Send


def send(filenames, chnglang, selections):
    for filename in filenames:
        _, language = os.path.splitext(filename)
        if chnglang:
            language = chnglang
        elif language == '':
            language = 'text'
        else:
            language = language[1:]
        source = MontoSource()
        try:
            source.publish_version(
                os.path.abspath(filename),
                language,
                open(filename).read(),
                selections
            )
        except OSError as err:
            error('error publishing version of {0}: {1}'.format(
                filename, err.strerror))


# Startup

if __name__ == '__main__':
    main()
