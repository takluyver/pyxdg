.. module:: xdg.Menu

Desktop Menu
============

`XDG Desktop Menu specification <http://standards.freedesktop.org/menu-spec/menu-spec-1.0.html>`_

.. autofunction:: parse

.. autoclass:: Menu
   :members: getName, getGenericName, getIcon, getComment, getPath, getEntries, getMenu, getMenuEntry

.. autoclass:: MenuEntry
   :members: save, getDir, getType
   
   .. attribute:: DesktopEntry
   
       The :class:`xdg.DesktopEntry.DesktopEntry` instance holding the data for this
       entry.
