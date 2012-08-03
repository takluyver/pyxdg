.. module:: xdg.DesktopEntry

Desktop Entries
===============

`XDG Desktop Entry Specification <http://standards.freedesktop.org/desktop-entry-spec/latest/>`_

.. autoclass:: DesktopEntry
   :members: __init__, new, parse, validate, 
   
DesktopEntry also has  get* methods for most values: getActions,
getBinaryPattern, getCategories, getComment, getDefaultApp, getDev,
getDocPath, getEncoding, getExec, getExtensions, getFSType, getFileName,
getFilePattern, getGenericName, getHidden, getIcon, getInitialPreference,
getKeywords, getList, getMapNotify, getMimeTypes, getMiniIcon, getMountPoint,
getName, getNoDisplay, getNotShowIn, getOnlyShowIn, getPath, getProtocols,
getReadonly, getServiceTypes, getSortOrder, getStartupNotify, getStartupWMClass,
getSwallowExec, getSwallowTitle, getTerminal, getTerminalOptions, getTryExec,
getType, getURL, getUnmountIcon and getVersionString.
