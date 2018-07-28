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
            return os.path.abspath(exe)
        for ext in [''] + os.environ.get('PATHEXT', '').split(os.pathsep):
            exe = '{}{}'.format(exe, ext.lower())
            if is_executable(exe):
                return os.path.abspath(exe)


def parse_python(value):
    if os.path.isabs(value):
        return str(value)
    full = which(value)
    if full:
        return full
    import pythonfinder
    python = pythonfinder.Finder().find_python_version(value)
    if python:
        return str(python.path)
    raise ValueError('invalid Python specification')


def ensure_directory(value):
    if os.path.exists(value):
        raise ValueError('path exists')
    return value


def main(args=None):
    parser = argparse.ArgumentParser(
        prog='virtenv',
        description='Create a virtual environment with venv or virtualenv.',
    )
    parser.add_argument(
        'env_dir', type=ensure_directory,
        help='Directory to create the virtual environment in.',
    )
    parser.add_argument(
        '--python', required=True, type=parse_python,
        help='Python to use (a version, command, or path to the executable).',
    )
    parser.add_argument(
        '--system-site-packages', default=False, action='store_true',
        help='Give the environment access to the system site-packages.',
    )
    parser.add_argument(
        '--prompt', default=None,
        help='Provides an alternative prompt prefix for this environment.',
    )
    opts = parser.parse_args(args)
    try:
        create(opts.python, opts.env_dir, opts.system, opts.prompt)
    except VirtualenvNotFound:
        print('virtualenv not available')
        sys.exit(1)


if __name__ == '__main__':
    main()
