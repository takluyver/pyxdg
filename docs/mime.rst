.. module:: xdg.Mime

Shared MIME-info Database
=========================

`XDG Shared MIME-info Database specification <http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html>`_

Finding a file's Mime type
--------------------------

Example::

    >>> Mime.get_type2('/path/to/foo.zip')
    MIMEtype('application', 'zip')

.. autofunction:: get_type2

.. autofunction:: get_type_by_name

.. autofunction:: get_type_by_contents

.. autofunction:: get_type_by_data

.. autofunction:: get_type

Installing Mime data
--------------------

.. autofunction:: install_mime_info

MIMEtype objects
----------------

.. autoclass:: MIMEtype
   :members: canonical, inherits_from
   
   .. versionchanged:: 1.0
      The class now takes care of caching; call :func:`lookup` in earlier versions.
   
   .. attribute:: media
   
      e.g. 'text'
   
   .. attribute:: subtype
      
      e.g. 'plain'
      
   .. automethod:: get_comment
   
   .. versionadded:: 0.25
      :meth:`MIMEtype.canonical` and :meth:`MIMEtype.inherits_from`.

.. autofunction:: lookup

Miscellaneous
-------------

.. autofunction:: get_extensions

.. autofunction:: is_text_file
