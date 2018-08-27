import argparse
import os
import sys

from virtenv import VirtualenvNotFound, create, get_script


def get_virtualenv_py():
    try:
        import virtualenv
    except ImportError:
        return None
    return get_script(virtualenv)


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


class Python(object):
    """Custom type to parse Python path.
    """
    def __repr__(self):
        return 'Python specification'

    def __call__(self, value):
        if os.path.isabs(value):
            return str(value)
        full = which(value)
        if full:
            return full
        import pythonfinder
        python = pythonfinder.Finder().find_python_version(value)
        if python:
            return str(python.path)
        raise ValueError(value)


class NonExistPath(object):
    """Custom type to ensure the value does not exist.
    """
    def __init__(self, parser):
        self.parser = parser

    def __repr__(self):
        return 'path'

    def __call__(self, value):
        if os.path.exists(value):
            self.parser.error('path exists at {!r}'.format(value))
        return value


def main(args=None):
    parser = argparse.ArgumentParser(
        prog='virtenv',
        description='Create a virtual environment with venv or virtualenv.',
    )
    parser.add_argument(
        'env_dir', type=NonExistPath(parser),
        help='Directory to create the virtual environment in.',
    )
    parser.add_argument(
        '--python', required=True, type=Python(),
        help='Python to use (a version, command, or path to the executable).',
    )
    parser.add_argument(
        '--system-site-packages', dest='system',
        default=False, action='store_true',
        help='Give the environment access to the system site-packages.',
    )
    parser.add_argument(
        '--prompt', default=None,
        help='Provides an alternative prompt prefix for this environment.',
    )
    opts = parser.parse_args(args)
    try:
        create(
            opts.python, opts.env_dir,
            opts.system, opts.prompt,
            get_virtualenv_py(),
        )
    except VirtualenvNotFound:
        print('virtualenv not available')
        sys.exit(1)


if __name__ == '__main__':
    main()
