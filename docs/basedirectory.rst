.. module:: xdg.BaseDirectory

Base Directories
================

The `XDG Base Directory specification <http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_
provides standard locations to store application data, configuration, and cached
data.

Data directories
----------------

.. autofunction:: save_data_path

.. autofunction:: load_data_paths

.. data:: xdg_data_home

   $XDG_DATA_HOME or the default, ``~/.local/share``

.. data:: xdg_data_dirs

   A list of directory paths in which application data may be stored, in
   preference order.

Configuration directories
-------------------------

.. autofunction:: save_config_path

.. autofunction:: load_config_paths

.. autofunction:: load_first_config

.. data:: xdg_config_home

   $XDG_CONFIG_HOME or the default, ``~/.config``

.. data:: xdg_config_dirs

   A list of directory paths in which configuration may be stored, in preference
   order.


Cache directory
---------------

.. autofunction:: save_cache_path

.. data:: xdg_cache_home

   $XDG_CACHE_HOME or the default, ``~/.cache``

Runtime directory
-----------------

.. autofunction:: get_runtime_dir
