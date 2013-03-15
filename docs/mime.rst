.. module:: xdg.Mime

Shared MIME-info Database
=========================

`XDG Shared MIME-info Database specification <http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html>`_

Finding a file's Mime type
--------------------------

Example::

    >>> Mime.get_type('/path/to/foo.zip')
    <application/zip: (comment not loaded)>

.. autofunction:: get_type

.. autofunction:: get_type_by_name

.. autofunction:: get_type_by_contents

.. autofunction:: get_type_by_data

.. autofunction:: get_extensions

Installing Mime data
--------------------

.. autofunction:: install_mime_info

MIMEtype objects
----------------

.. autofunction:: lookup

.. autoclass:: MIMEtype
   :members: canonical, inherits_from
   
   .. attribute:: media
   
      e.g. 'text'
   
   .. attribute:: subtype
      
      e.g. 'plain'
      
   .. automethod:: get_comment
   
   .. versionadded:: 0.25
      :meth:`MIMEtype.canonical` and :meth:`MIMEtype.inherits_from`.
