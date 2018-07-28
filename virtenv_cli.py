import argparse
import os
import sys

from virtenv import VirtualenvNotFound, create


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def which(name):
    for p in os.environ['PATH'].split(os.pathsep):
        exe = os.path.join(p, name)
        if is_executable(exe):
            return exe
        for ext in [''] + os.environ.get('PATHEXT', '').split(os.pathsep):
            exe = '{}{}'.format(exe, ext.lower())
            if is_executable(exe):
                return exe


def parse_python(value):
    if os.path.abspath(value):
        return str(value)
    full = which(value)
    if full:
        return full
    import pythonfinder
    python = pythonfinder.Finder().find_python_version(value)
    if python:
        return str(python.path)
    raise ValueError('invalid Python specification')


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('env_dir')
    parser.add_argument('--python', required=True, type=parse_python)
    parser.add_argument('--system', default=False, action='store_true')
    parser.add_argument('--prompt', default=None)
    opts = parser.parse_args(args)
    try:
        create(opts.python, opts.env_dir, opts.system, opts.script)
    except VirtualenvNotFound:
        print('virtualenv not available')
        sys.exit(1)


if __name__ == '__main__':
    main()
