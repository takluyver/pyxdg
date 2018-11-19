# coding: utf-8
"""This file contains sample data for the test suite - these are
written out to temporary files for the relevant tests.
"""
from __future__ import unicode_literals

import sys

# With additions from firefox.desktop, to test locale & unicode support
gedit_desktop = """[Desktop Entry]
Name=gedit
Name[ar]=متصفح الوِب فَيَرفُكْس
GenericName=Text Editor
Comment= Edit text files
Keywords=Plaintext;Write;
Keywords[ja]=Internet;WWW;Web;インターネット;ブラウザ;ウェブ;エクスプローラ
Exec=gedit %U
Terminal=false
Type=Application
StartupNotify=true
MimeType=text/plain;
Icon=accessories-text-editor
Categories=GNOME;GTK;Utility;TextEditor;
X-GNOME-DocPath=gedit/gedit.xml
X-GNOME-FullName=Text Editor
X-GNOME-Bugzilla-Bugzilla=GNOME
X-GNOME-Bugzilla-Product=gedit
X-GNOME-Bugzilla-Component=general
X-GNOME-Bugzilla-Version=3.4.1
X-GNOME-Bugzilla-ExtraInfoScript=/usr/share/gedit/gedit-bugreport
Actions=Window;Document;
X-Ubuntu-Gettext-Domain=gedit

[Desktop Action Window]
Name=Open a New Window
Exec=gedit --new-window
OnlyShowIn=Unity;

[Desktop Action Document]
Name=Open a New Document
Exec=gedit --new-window
OnlyShowIn=Unity;
"""

# Unicode, + TryExec that doesn't exist
unicode_desktop = """[Desktop Entry]
Name=Abc€þ
Type=Application
Exec=date
TryExec=ewoirjge
"""

# Invalid - see the Categories line
spout_desktop = """[Desktop Entry]
Type=Application
Encoding=UTF-8
Name=Spout
GenericName=
Comment=
Icon=spout
Exec=/usr/games/spout
Terminal=false
Categories:Application:Game:ArcadeGame
"""

# Test with invalid UTF-8
gnome_alsamixer_desktop = """[Desktop Entry]
Name=GNOME ALSA Mixer
Comment=ALSA sound mixer for GNOME
Comment[es]=Mezclador de sonido ALSA para GNOME
Comment[fr]=Mélangeur de son ALSA pour GNOME
Exec=gnome-alsamixer
Type=Application
"""

# TryExec that should exist
python_desktop = """[Desktop Entry]
Name=Python
Comment=Dynamic programming language
Exec=%s
TryExec=%s
Type=Application
""" % (sys.executable, sys.executable)

recently_used = """<?xml version="1.0"?>
<RecentFiles>
<RecentItem>
<URI>file:///home/thomas/foo/bar.ods</URI>
<Mime-Type>application/vnd.oasis.opendocument.spreadsheet</Mime-Type>
<Timestamp>1272385187</Timestamp>
<Groups>
<Group>openoffice.org</Group>
<Group>staroffice</Group>
<Group>starsuite</Group>
</Groups>
</RecentItem>
<RecentItem>
<URI>file:///tmp/2.ppt</URI>
<Mime-Type>application/vnd.ms-powerpoint</Mime-Type>
<Timestamp>1272378716</Timestamp>
<Groups>
<Group>openoffice.org</Group>
<Group>staroffice</Group>
<Group>starsuite</Group>
</Groups>
</RecentItem>
</RecentFiles>
"""

applications_menu = """<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
 "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">

<Menu>

  <Name>Applications</Name>
  <Directory>X-GNOME-Menu-Applications.directory</Directory>

  <!-- Scan legacy dirs first, as later items take priority -->
  <LegacyDir>/etc/X11/applnk</LegacyDir>
  <LegacyDir>/usr/share/gnome/apps</LegacyDir>

  <!-- Read standard .directory and .desktop file locations -->
  <DefaultAppDirs/>
  <DefaultDirectoryDirs/>

  <!-- Read in overrides and child menus from applications-merged/ -->
  <DefaultMergeDirs/>

  <!-- Accessories submenu -->
  <Menu>
    <Name>Accessories</Name>
    <Directory>Utility.directory</Directory>
    <Include>
      <And>
        <Category>Utility</Category>
	<!-- Accessibility spec must have either the Utility or Settings
	     category, and we display an accessibility submenu already for
	     the ones that do not have Settings, so don't display accessibility
	     applications here -->
        <Not><Category>Accessibility</Category></Not>
        <Not><Category>System</Category></Not>
      </And>
    </Include>
  </Menu> <!-- End Accessories -->

  <!-- Accessibility submenu -->
  <Menu>
    <Name>Universal Access</Name>
    <Directory>Utility-Accessibility.directory</Directory>
    <Include>
      <And>
        <Category>Accessibility</Category>
        <Not><Category>Settings</Category></Not>
      </And>
    </Include>
  </Menu> <!-- End Accessibility -->

  <!-- Development Tools -->
  <Menu>
    <Name>Development</Name>
    <Directory>Development.directory</Directory>
    <Include>
      <And>
        <Category>Development</Category>
      </And>
      <Filename>emacs.desktop</Filename>
    </Include>
  </Menu> <!-- End Development Tools -->

  <!-- Education -->
  <Menu>
    <Name>Education</Name>
    <Directory>Education.directory</Directory>
    <Include>
      <And>
        <Category>Education</Category>
        <Not><Category>Science</Category></Not>
      </And>
    </Include>
  </Menu> <!-- End Education -->

  <!-- Science -->
  <Menu>
    <Name>Science</Name>
    <Directory>GnomeScience.directory</Directory>
    <Include>
      <And>
        <Category>Education</Category>
        <Category>Science</Category>
      </And>
    </Include>
  </Menu> <!-- End Science -->

  <!-- Games -->
  <Menu>
    <Name>Games</Name>
    <Directory>Game.directory</Directory>
    <Include>
      <And>
        <Category>Game</Category>
        <Not><Category>ActionGame</Category></Not>
        <Not><Category>AdventureGame</Category></Not>
        <Not><Category>ArcadeGame</Category></Not>
        <Not><Category>BoardGame</Category></Not>
        <Not><Category>BlocksGame</Category></Not>
        <Not><Category>CardGame</Category></Not>
        <Not><Category>KidsGame</Category></Not>
        <Not><Category>LogicGame</Category></Not>
        <Not><Category>Simulation</Category></Not>
        <Not><Category>SportsGame</Category></Not>
        <Not><Category>StrategyGame</Category></Not>
      </And>
    </Include>
    <DefaultLayout inline="true" inline_limit="6" inline_header="false">
      <Merge type="menus"/>
      <Merge type="files"/>
    </DefaultLayout>
    <Menu>
      <Name>Action</Name>
      <Directory>ActionGames.directory</Directory>
      <Include>
        <Category>ActionGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Adventure</Name>
      <Directory>AdventureGames.directory</Directory>
      <Include>
        <Category>AdventureGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Arcade</Name>
      <Directory>ArcadeGames.directory</Directory>
      <Include>
        <Category>ArcadeGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Board</Name>
      <Directory>BoardGames.directory</Directory>
      <Include>
        <Category>BoardGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Blocks</Name>
      <Directory>BlocksGames.directory</Directory>
      <Include>
        <Category>BlocksGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Cards</Name>
      <Directory>CardGames.directory</Directory>
      <Include>
        <Category>CardGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Kids</Name>
      <Directory>KidsGames.directory</Directory>
      <Include>
        <Category>KidsGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Logic</Name>
      <Directory>LogicGames.directory</Directory>
      <Include>
        <Category>LogicGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Role Playing</Name>
      <Directory>RolePlayingGames.directory</Directory>
      <Include>
        <Category>RolePlaying</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Simulation</Name>
      <Directory>SimulationGames.directory</Directory>
      <Include>
        <Category>Simulation</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Sports</Name>
      <Directory>SportsGames.directory</Directory>
      <Include>
        <Category>SportsGame</Category>
      </Include>
    </Menu>
    <Menu>
      <Name>Strategy</Name>
      <Directory>StrategyGames.directory</Directory>
      <Include>
        <Category>StrategyGame</Category>
      </Include>
    </Menu>
  </Menu> <!-- End Games -->

  <!-- Graphics -->
  <Menu>
    <Name>Graphics</Name>
    <Directory>Graphics.directory</Directory>
    <Include>
      <And>
        <Category>Graphics</Category>
      </And>
    </Include>
  </Menu> <!-- End Graphics -->

  <!-- Internet -->
  <Menu>
    <Name>Internet</Name>
    <Directory>Network.directory</Directory>
    <Include>
      <And>
        <Category>Network</Category>
      </And>
    </Include>
  </Menu>   <!-- End Internet -->

  <!-- Multimedia -->
  <Menu>
    <Name>Multimedia</Name>
    <Directory>AudioVideo.directory</Directory>
    <Include>
      <And>
        <Category>AudioVideo</Category>
      </And>
    </Include>
  </Menu>   <!-- End Multimedia -->

  <!-- Office -->
  <Menu>
    <Name>Office</Name>
    <Directory>Office.directory</Directory>
    <Include>
      <And>
        <Category>Office</Category>
      </And>
    </Include>
  </Menu> <!-- End Office -->

  <!-- System Tools-->
  <Menu>
    <Name>System</Name>
    <Directory>System-Tools.directory</Directory>
    <Include>
      <And>
        <Category>System</Category>
        <Not><Category>Settings</Category></Not>
	<Not><Category>Game</Category></Not>
      </And>
    </Include>
    <Menu>
      <Name>Preferences</Name>
      <Directory>Settings.directory</Directory>
      <Include>
        <And>
          <Category>Settings</Category>
          <Not>
            <Or>
              <Category>System</Category>
              <Category>X-GNOME-Settings-Panel</Category>
            </Or>
          </Not>
        </And>
      </Include>
    </Menu>
    <Menu>
      <Name>Administration</Name>
      <Directory>Settings-System.directory</Directory>
      <Include>
        <And>
          <Category>Settings</Category>
          <Category>System</Category>
          <Not>
            <Category>X-GNOME-Settings-Panel</Category>
          </Not>
        </And>
      </Include>
    </Menu>
  </Menu>   <!-- End System Tools -->

  <!-- Other -->
  <Menu>
    <Name>Other</Name>
    <Directory>X-GNOME-Other.directory</Directory>
    <OnlyUnallocated/>
    <Include>
      <And>
        <Not><Category>Core</Category></Not>
        <Not><Category>Screensaver</Category></Not>
        <Not><Category>X-GNOME-Settings-Panel</Category></Not>
      </And>
    </Include>
  </Menu> <!-- End Other -->

   <Layout>
     <Merge type="menus" />
     <Menuname>Other</Menuname>
     <Merge type="files" />
   </Layout>

  <!-- The Debian menu -->
  <Menu>
    <Name>Debian</Name>
    <MergeFile>debian-menu.menu</MergeFile>
    <Directory>Debian.directory</Directory>
  </Menu>

<Include>
  <Filename>ubuntu-software-center.desktop</Filename>
</Include>

<!-- Separator between menus and gnome-app-install -->
<Layout>
  <Merge type="menus"/>
  <Merge type="files"/>
  <Separator/>
  <Filename>ubuntu-software-center.desktop</Filename>
</Layout>

</Menu> <!-- End Applications -->
"""

legacy_menu = """<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
 "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">

<Menu>

  <Name>Legacy</Name>
  <LegacyDir>legacy_dir</LegacyDir>

</Menu>
"""

kde_legacy_menu = """<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
 "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">

<Menu>

  <Name>KDE Legacy</Name>
  <KDELegacyDirs/>

</Menu>
"""

layout_menu = """<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
 "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">
<Menu>

  <Name>Layout</Name>
  <DefaultLayout show_empty="true">
    <Merge type="menus"/>
    <Merge type="files"/>
    <Separator/>
    <Menuname>More</Menuname>
  </DefaultLayout>

  <Menu>
    <Name>More</Name>
  </Menu>

  <Menu>
    <Name>Games</Name>
    <Layout>
      <Menuname>Steam</Menuname>
      <Separator/>
      <Merge type="menus"/>
    </Layout>
    <Menu>
      <Name>Action</Name>
    </Menu>
    <Menu>
      <Name>Steam</Name>
    </Menu>
    <Menu>
      <Name>Arcade</Name>
    </Menu>
  </Menu>

  <Menu>
    <Name>Accessories</Name>
  </Menu>
</Menu>
"""

mime_globs2_a = """#globs2 MIME data file
55:text/x-diff:*.patch
50:text/x-c++src:*.C:cs
50:text/x-python:*.py
10:text/x-readme:readme*
"""

mime_globs2_b = """#globs2 MIME data file
# Add to existing MIMEtype
50:text/x-diff:*.diff
# Remove one
50:text/x-python:__NOGLOBS__
# Replace one
40:text/x-readme:__NOGLOBS__
20:text/x-readme:RDME:cs
"""

mime_magic_db = b"""MIME-Magic\0
[50:image/png]
>0=\0\x04\x89PNG
[50:image/jpeg]
>0=\0\x03\xff\xd8\xff
>0=\0\x02\xff\xd8
[50:image/openraster]
>0=\0\x04PK\x03\x04
1>30=\0\x08mimetype
2>38=\0\x10image/openraster
[80:image/svg+xml]
>0=\0\x0d<!DOCTYPE svg+257
>0=\0\x04<svg+257
[50:image/vnd.adobe.photoshop]
>0=\0\x0a8BPS  \0\0\0\0&\xff\xff\xff\xff\0\0\xff\xff\xff\xff
[40:application/x-executable]
>0=\0\02\x01\x11~2
[10:application/madeup]
>0=\0\x05ab
cd
>10=\0\x05ab de&\xff\xff
\xff\xff
[10:application/imaginary]
>0=\0\x03abc@unhandled_future_field
[10:application/toberemoved]
>0=\0\x03def
[10:application/tobereplaced]
>0=\0\x03ghi
[10:application/tobeaddedto]
>0=\0\x03mno
"""

mime_magic_db2 = b"""MIME-Magic\0
[10:application/toberemoved]
>0=__NOMAGIC__
[10:application/tobereplaced]
>0=__NOMAGIC__
>1=\0\x03jkl
[10:application/tobeaddedto]
>1=\0\x03pqr
"""

png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\rIDAT\x08\x99c\xf8\x7f\x83\xe1?\x00\x07\x88\x02\xd7\xd9\n\xd8\xdc\x00\x00\x00\x00IEND\xaeB`\x82'

icon_data = """[Icon Data]
DisplayName=Mime text/plain
EmbeddedTextRectangle=100,100,900,900
AttachPoints=200,200|800,200|500,500|200,800|800,800
"""
