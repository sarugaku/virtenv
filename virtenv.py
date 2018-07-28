from __future__ import print_function

__all__ = ['create', 'VirtualenvNotFound']

import os
import subprocess
import sys

try:
    import venv
except ImportError:
    venv = None
else:
    class _EnvBuilder(venv.EnvBuilder):
        """Custom environment builder to ensure libraries are up-to-date.

        Also add support to custom prompt, and some output to make the process
        more verbose, matching virtualenv's behavior.
        """
        def __init__(self, **kwargs):
            if sys.version_info < (3, 6):
                self.prompt = kwargs.pop('prompt', None)
            super(_EnvBuilder, self).__init__(**kwargs)

        def ensure_directories(self, env_dir):
            context = super(_EnvBuilder, self).ensure_directories(env_dir)
            if sys.version_info < (3, 6) and self.prompt is not None:
                context.prompt = self.prompt
            return context

        def setup_python(self, context):
            super(_EnvBuilder, self).setup_python(context)
            print('New Python executable in', context.env_exe)

        def post_setup(self, context):
            print('Ensuring up-to-date setuptools, pip, and wheel...',
                  end='', flush=True)
            returncode = subprocess.call([
                context.env_exe, '-m', 'pip', 'install',
                '--upgrade', '--disable-pip-version-check', '--quiet',
                'setuptools', 'pip', 'wheel',
            ])
            if returncode == 0:
                print('done')
            else:
                # If update fails, there should already be a nice error message
                # from pip present. Just carry on.
                print()


def _get_script(module=None):
    if module:
        script = os.path.abspath(module.__file__)
    else:
        script = os.path.abspath(__file__)
    if script.endswith('.pyc'):
        script = script[:1]
    return script


def create_venv(env_dir, system_site_packages, prompt):
    builder = _EnvBuilder(
        prompt=prompt,  # Supported by custom builder.
        system_site_packages=system_site_packages,
        symlinks=(os.name != 'nt'),  # Copied from venv logic.
        with_pip=True,  # We only enter here for Python 3.4+ so this is fine.
    )
    builder.create(env_dir)


class VirtualenvNotFound(EnvironmentError):
    pass


def create_virtualenv(virtualenv_py, env_dir, system, prompt):
    if not virtualenv_py:
        try:
            import virtualenv
        except ImportError:
            raise VirtualenvNotFound
        else:
            virtualenv_py = _get_script(virtualenv)
    cmd = [sys.executable, virtualenv_py, str(env_dir)]
    if system:
        cmd.append('--system-site-packages')
    if prompt:
        cmd.extend(['--prompt', prompt])
    subprocess.check_call(cmd)


def _is_venv_usable():
    if not venv:
        if sys.version_info >= (3, 3):
            print('venv not available, falling back to virtualenv')
        else:
            print('Using virtualenv')
        return False
    try:
        import ensurepip    # noqa
    except ImportError:
        print('venv without ensurepip is unuseful, falling back to virtualenv')
        return False
    try:
        sys.real_prefix
    except AttributeError:
        print('Using venv')
        return True
    print('venv breaks when nesting in virtualenv, falling back to virtualenv')
    return False


def _create_with_this(env_dir, system, prompt, virtualenv_py):
    if _is_venv_usable():
        create_venv(env_dir, system, prompt)
    else:
        create_virtualenv(virtualenv_py, env_dir, system, prompt)


def _create_with_python(python, env_dir, system, prompt, virtualenv_py):
    # Delegate everything into a subprocess. Trick learned from virtualenv.
    cmd = [python, _get_script(), str(env_dir), '--prompt', prompt]
    if system:
        cmd.append('--system')
    if virtualenv_py:
        cmd.extend(['--virtualenv.py', virtualenv_py])
    subprocess.check_call(cmd)


def create(python, env_dir, system, prompt, virtualenv_py=None):
    """Main entry point to use this as a module.
    """
    if not python or python == sys.executable:
        _create_with_this(env_dir, system, prompt, virtualenv_py)
    else:
        _create_with_python(python, env_dir, system, prompt, virtualenv_py)


def _main(args=None):
    # Handles the delegation from _create_with_python.
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('env_dir')
    parser.add_argument('--system', default=False, action='store_true')
    parser.add_argument('--virtualenv.py', dest='script', default=None)
    parser.add_argument('--prompt', default=None)
    opts = parser.parse_args(args)
    try:
        _create_with_this(opts.env_dir, opts.system, opts.prompt, opts.script)
    except VirtualenvNotFound:
        print('virtualenv not available')
        sys.exit(1)


if __name__ == '__main__':
    _main()
