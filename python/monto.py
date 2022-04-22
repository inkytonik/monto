#! /usr/bin/env python3
# Monto command

import getopt
import multiprocessing
import pathlib
import os
import psutil
import signal
import subprocess
import sys
import tempfile
import montolib

# Main program


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    except getopt.GetoptError as err:
        montolib.error(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'
    numargs = len(args)
    config = montolib.monto_read_config()
    if numargs == 0:
        command = 'start'
    elif numargs >= 1:
        command = args[0]
    if numargs <= 1:
        if command == 'restart':
            stop(config)
            start(config)
        if command == 'start':
            start(config, set())
        elif command == 'status':
            status(config)
        elif command == 'stop':
            stop(config)
        else:
            montolib.error('unknown command \'{0}\''.format(command))
            usage()
    else:
        if command == 'start':
            start(config, set(args[1:]))
        else:
            montolib.error('unknown command \'{0}\''.format(' '.join(args)))
            usage()


def usage():
    print('usage: monto [-h] [command]')
    print('  commands: restart, start [set...] (default), status, stop')

# Management of lock file that contains PIDs of broker and programs


def pid_file_path():
    return pathlib.Path(os.path.join(tempfile.gettempdir(), 'monto.pids'))


def monto_is_running():
    return pid_file_path().is_file()


def add_pid(pid):
    with pid_file_path().open('a') as file:
        file.write('{0}\n'.format(pid))


def get_pids():
    with pid_file_path().open('r') as file:
        contents = file.read()
        pids = []
        for line in contents.split('\n'):
            if line:
                try:
                    pid = int(line)
                    pids.append(pid)
                except ValueError:
                    montolib.error(
                        'bad line in {0}: {1}'.format(pid_file_path(), line))
                    sys.exit(4)
        return pids


def kill_all_pids():
    for pid in get_pids():
        try:
            if sys.platform == "win32":
                os.kill(pid, signal.SIGBREAK)
            else:
                os.killpg(pid, signal.SIGTERM)
        except ProcessLookupError:
            montolib.error('process {0!s} does not exist'.format(pid))


def remove_pid_file():
    pid_file_path().unlink()

# Start command


def start(config, sets):
    if monto_is_running():
        print('monto is already running')
    else:
        programs = []
        if 'programs' in config:
            programs = config['programs']
            for program in programs:
                run_command(config, program, sets)
        status(config)


def run_command(config, program, sets):
    cwd = program.get('directory', '.')
    if should_run(program, sets):
        try:
            process = subprocess.Popen(
                args=program['command'],
                cwd=cwd,
                env=os.environ,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                start_new_session=True
            )
            add_pid(process.pid)
        except OSError as err:
            montolib.error('can\'t run program {0}: {1}'.format(
                program['command'], err.strerror))


def should_run(program, sets):
    if 'command' in program:
        return not(bool(sets)) or 'sets' not in program or bool(sets.intersection(program['sets']))
    else:
        print('monto: source missing command, ignoring:')
        print(program)

# Status command


def status(config):
    if monto_is_running():
        print('monto is running')
        pids = get_pids()
        if len(pids) == 0:
            print('  no programs')
        else:
            print('  programs:')
            for pid in pids:
                print('    {0}'.format(process_desc(pid)))
    else:
        print('monto is not running')


def process_desc(pid):
    try:
        p = psutil.Process(pid)
        cmdline = ' '.join(p.cmdline())
        desc = cmdline[cmdline.rfind('/') + 1:]
        return desc
    except psutil.NoSuchProcess:
        return 'no process ({0!s})'.format(pid)

# Stop command


def stop(config):
    if monto_is_running():
        kill_all_pids()
        remove_pid_file()
        print('monto has been stopped')
    else:
        print('monto is not running')

# Startup

if __name__ == '__main__':
    main()
