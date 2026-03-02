<img width="708" height="635" alt="Picture_created_02-03-2026_03-26-06" src="https://github.com/user-attachments/assets/801f3d8c-561a-4669-b76a-ac74e5f85e5e" />

# Screenshot of the tool
Many devs don't include a screenshot of their own creation and you gotta turn Google upside down till you find something. I won't be like this, so here's a screenshot of the GTK3 version with my dark theme.

# Arch Updates simple GUI tool
A simple python GUI tool that checks for updates and shows them. This tool is simply for information, intended to replace tools like Octopi.
It's written in Python3 and like everything else I share in my repositories, it's FOSS with MIT license meaning you're free to do whatever you want with it, including change the code or even completely rewrite it.

# What is the tool for?
Arch Updates GUI is for Arch and all Arch-based distros that use pacman as a package manager.

# What the tool DOESN'T & CAN'T do?
Update the packages. It's only informational, it can't do anything you didn't tell it to do.
The tool CAN'T check for updates in AUR but I suppose you could make it look in there too, if you want.

# What the tool CAN do?
When you run it, it automatically runs the command 'checkupdates' and displays all the packages waiting to be updated.
It displays package name, current version and new version.
The tool's collumns' sizes are fixed (but you can edit them in the '.py' file yourself, if you want. I suppose I could have added an option to drag and resize these collumns but I wanted to keep it as simple as possible on purpose. The less complications in the code - the less likely for something to stop working.

# What the tool does?
Aside from the checking updates, Arch Updates GUI reads the
```
IgnorePkg = 
```
line in /etc/pacman.conf.
If it finds any package mentioned there, the tool WON'T show it in the list of packages waiting to be updated. If you wanna see that package there, you're gonna have to remove it from IgnorePkg first.

# Dependencies (more accurate)

The tool has only a few dependencies, and none of them require a specific version:

For the GTK3/GTK4 version:

    Python 3

    PyGObject (for GTK3/GTK4)

For the Qt5/Qt6 version:

    Python 3

    PyQt5 or PySide2 (Qt5)

    PyQt6 or PySide6 (Qt6)

Any installed version of these frameworks is fine — the tool does not depend on exact versions.

# No compiling - full transparency
Python is one of the few programming languages that can work without being compiled, therefore the .py files don't need to be compiled and can be edited at anytime by anyone!

# Languages
Currently (and probably forever) the languages available are Bulgarian (because I'm Bulgarian :) ) and English. For each language you're gonna have to download the archive with the desired suffix "_EN" or "_BG".
If your language isn't there, you can edit the 3 strings and translate them to your target language.

# Interfaces
The interfaces of the tool are GTK3 and QT6.
I have only tested the GTK3 version and it works perfectly!
The GTK3 version can easily be changed into GTK4 by simply changing the number "3.0" of this line:

```
gi.require_version("Gtk", "3.0")
```
to be "4.0" and that's it.

# The QT6 version hasn't been tested
Feel free to do that, if you're using Plasma.
In the same manner the QT6 version SHOULD be possible to be changed into QT5 by changing the number of these lines:

```
PyQt6.QtWidgets
PyQt6.QtCore
```
and make them look like this:

```
PyQt5.QtWidgets
PyQt5.QtCore
```
BUT!!! take a note this is just a theory. I'm not a big fan of the QT framework, so I've never tested any of it - not the QT6 tool itself, not the possibility to change it into QT5.

# .desktop file & an icon
I decided to leave that to you because what I like for an icon you may or may not like.

# Some ideas
Since the tool is run by the bash script that is included in the archive, you can:
• set it to autostart with the system
• set it to run at specific intervals, if you know how to use cronjob (I don't)

# Why this tool exists?
Because I couldn't find anything better that wasn't seriously outdated and that would show me only what I wanted - without any bloated functions. Octopi is outdated and unclear, 99% of its functions and options don't work properly, the pamac series are pretty much the same - the interface works but not much else of them.

# Questions and problems
If you have any questions or problems, post an issue and I'll answer/try to help.
