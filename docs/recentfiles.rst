.. module:: xdg.RecentFiles

Recently used files
===================

`XDG recent file storage specification <http://standards.freedesktop.org/recent-file-spec/recent-file-spec-latest.html>`_

.. autoclass:: RecentFiles
   :members: parse, write, getFiles, addFile, deleteFile

.. class:: RecentFile

   .. attribute:: URI
      
      The URI of the file; typically starts with ``file:///``.
    
   .. attribute:: MimeType
   
      A Mime type, such as 'text/plain'.
   
   .. attribute:: Timestamp
   
      Unix timestamp of when the file was added to the list.
   
   .. attribute:: Private
   
      Boolean indicating whether the entry is private, meaning that it will only
      be shown if it is in a selected group.
   
   .. attribute:: Groups
   
      A list of groups this entry belongs to.
