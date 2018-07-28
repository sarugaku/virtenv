=======
VirtEnv
=======

A simple script to encapsulate venv and virtualenv creation in one. venv is
always used if possible; if it's not, virtualenv will be used (if specified)
as the fallback option.

This file can be used either as a standalone script, or a module to import.


Python API
==========

::

    create(python, env_dir, virtualenv_py, system, prompt)

* ``python`` should be an absolute path pointing to a Python executable. If
  this is not ``None``, and does not match ``sys.executable``, that interpreter
  is launched as a subprocess to run this script. Otherwise, the creation is
  done in-process (subprocesses may still be run in steps during the creation).
* ``env_dir`` points to the directory to create the new virtual environment.
* ``system`` specifies whether system site packages will be available for
  the created virtual environment.
* ``prompt`` specifies the prompt prefix used in the created virtual
  environment's activate scripts.
* ``virtualenv_py`` should be an absolute path pointing to a ``virtualenv.py``
  script. This is optional; if missing, virtualenv will not be used to create
  a virtual environment.


Command line API
================

::

    virtenv env_dir --python PYTHON [--system] [--prompt PROMPT]

Meanings of arguments are similar to the Python API.

The ``python`` argument is required, and can be a version, such as ``3.7``.
A suitable Python executable will be looked up automatically if possible.


When is venv used
=================

As mentioned above, venv is always preferred *if possible*. virtualenv is used
for the following scenarios:

* When the module ``venv`` is not available in the target Python.
* When the module ``ensurepip`` is not available in the target Python. This
  generally happens for Python 3.3, or distributions such as Debian that don't
  like to bundle ``ensurepip``. Without it, pip wouldn't be available, and we
  don't want that.
* When ``sys.real_prefix`` is set. This usually means the target Python is
  managed by a virtualenv, and venv is known to have problems working in this
  situation. See discussion in `bpo-30811`_ and `pypa/virtualenv#1095`_ for
  more information.

.. _`bpo-30811`: https://bugs.python.org/issue30811
.. _`pypa/virtualenv#1095`: https://github.com/pypa/virtualenv/issues/1095
