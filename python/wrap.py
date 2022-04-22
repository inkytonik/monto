#! /usr/bin/env python3
# Wrap a shell command as a Monto server

import getopt
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import montolib

# Main program


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'mv:h', ['message', 'verslang', 'help'])
    except getopt.GetoptError as err:
        error(err)
        sys.exit(2)
    message = False
    verslang = None
    for o, a in opts:
        if o in ('-m', '--message'):
            message = True
        elif o in ('-v', '--verslang'):
            verslang = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'
    if len(args) < 3:
        error('not enough arguments')
    else:
        tmpfile = tempfile.mkstemp(suffix='.txt', text=True)
        wrap(verslang, message, args[0], args[1], args[2:], pathlib.Path(tmpfile[1]))
        os.unlink(tmpfile[1])


def error(msg):
    print('wrap: {0!s}'.format(msg))
    usage()


def usage():
    print('usage: wrap [-m] [-v verslang] product prodlang command args...')

# Wrapping


def wrap(verslang, message, product, prodlang, args, tmpfilepath):
    montolib.server(
        lambda c: run_command(product, message, prodlang, c, args, tmpfilepath),
        filter=verslang
    )


def run_command(product, message, prodlang, version, args, tmpfilepath):
    cmdstr = ' '.join(args)
    try:
        with tmpfilepath.open('w') as file:
            file.write(version['contents'])
        tmpfilename = str(tmpfilepath)
        stdinfd = os.open(tmpfilename, os.O_RDONLY)
        cmdargs = make_command_args(version, args, tmpfilename)
        output = subprocess.check_output(args=cmdargs, stdin=stdinfd)
        os.close(stdinfd)
        print(message)
        if message:
            wrap_product = {
                'source': version['source'],
                'product': 'message',
                'language': 'message',
                'contents': messages_from(output.decode())
            }
            return ([wrap_product], True)
        else:
            wrap_product = {
                'source': version['source'],
                'product': product,
                'language': prodlang,
                'contents': output.decode()
            }
            return ([wrap_product], True)
    except subprocess.CalledProcessError as err:
        wrap_product = {
            'source': version['source'],
            'product': product,
            'language': 'text A',
            'contents': err.output.decode()
        }
        return ([wrap_product], True)
    except Exception as err:
        wrap_product = {
            'source': version['source'],
            'product': product,
            'language': 'text B',
            'contents': 'Command \'{0}\' failed: {1!s}'.format(cmdstr, err)
        }
        return ([wrap_product], True)


def messages_from(text):
    x = re.split('([^:]+):([0-9]+):([0-9]+): (.*)', text)
    return str(x)


def make_command_args(version, args, tmpfilename):
    return map(lambda arg: replace_arg(version, arg, tmpfilename), args)


def replace_arg(version, arg, tmpfilename):
    replacements = {
        "$CONTENTS": tmpfilename,
        "$LANGUAGE": version['language'],
        "$SELECTION": montolib.get_selection_text(version),
        "$SOURCE": version['source']
    }
    return re.sub(r'(\$[A-Z]+)',
                  lambda m: replacements.get(m.group(0), m.group(0)),
                  arg)

# Startup

if __name__ == '__main__':
    main()
