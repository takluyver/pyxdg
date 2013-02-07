.. module:: xdg.DesktopEntry

Desktop Entries
===============

`XDG Desktop Entry Specification <http://standards.freedesktop.org/desktop-entry-spec/latest/>`_

.. autoclass:: DesktopEntry

   .. automethod:: __init__
   
   .. automethod:: new
   
   .. automethod:: parse
   
   .. automethod:: validate
   
   .. automethod:: findTryExec
   
      .. versionadded:: 0.26
   
   .. method:: getCategories
               getComment
               getExec
               getGenericName
               getHidden
               getIcon
               getMimeTypes
               getMiniIcon
               getName
               getNoDisplay
               getNotShowIn
               getOnlyShowIn
               getPath
               getProtocols
               getStartupNotify
               getStartupWMClass
               getTerminal
               getTerminalOptions
               getTryExec
               getType
               getURL
               getVersionString
   
     Convenience methods to get the values of specific fields. If the field is
     missing, these will simply return an empty or zero value. There are similar
     methods for deprecated and KDE specific keys, but these are not listed here.
