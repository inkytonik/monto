#! /usr/bin/env python3
# reflect
# Reflect a version back as a product.

import getopt
import sys
import montolib


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs', ['help', 'selection'])
    except getopt.GetoptError as err:
        error(err)
        sys.exit(1)
    useselection = False
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif o in ('-s', '--selection'):
            useselection = True
        else:
            assert False, 'unhandled option'
    if args == []:
        montolib.server(lambda version: version_reflect(version, useselection))
    else:
        error('too many arguments')
        sys.exit(3)


def error(msg):
    print('reflect: {0!s}'.format(msg))
    usage()


def usage():
    print('usage: reflect [-s]')


def version_reflect(version, useselection):
    if useselection:
        contents = montolib.get_selection_text(version)
    else:
        contents = version['contents']
    reflect_product = {
        'source': version['source'],
        'product': 'reflect',
        'language': version['language'],
        'contents': contents
    }
    return ([reflect_product], True)


# Startup

if __name__ == '__main__':
    main()
