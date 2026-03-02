#!/usr/bin/env python3
import gi
import subprocess
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

PACMAN_CONF = "/etc/pacman.conf"


def read_ignorepkg():
    ignore = set()
    pattern = re.compile(r"^\s*IgnorePkg\s*=\s*(.*)$")

    with open(PACMAN_CONF, "r") as f:
        for line in f:
            m = pattern.match(line)
            if m:
                pkgs = m.group(1).split()
                ignore.update(pkgs)

    return ignore


def get_updates():
    try:
        output = subprocess.check_output(["checkupdates"], text=True)
    except subprocess.CalledProcessError:
        return []

    updates = []
    for line in output.strip().split("\n"):
        if not line.strip():
            continue

        # Format: pkgname oldver -> newver
        parts = line.split()
        if len(parts) >= 4 and parts[2] == "->":
            pkg = parts[0]
            oldver = parts[1]
            newver = parts[3]
            updates.append((pkg, oldver, newver))

    return updates


class UpdateWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Arch Updates GTK3")
        self.set_default_size(700, 600)

        ignore = read_ignorepkg()
        updates = [u for u in get_updates() if u[0] not in ignore]

        liststore = Gtk.ListStore(str, str, str)
        for pkg, old, new in updates:
            liststore.append([pkg, old, new])

        treeview = Gtk.TreeView(model=liststore)

        renderer = Gtk.CellRendererText()

        col1 = Gtk.TreeViewColumn("Package name", renderer, text=0)
        col2 = Gtk.TreeViewColumn("Current version", renderer, text=1)
        col3 = Gtk.TreeViewColumn("New version", renderer, text=2)

        col1.set_fixed_width(300)
        col2.set_fixed_width(200)
        col3.set_fixed_width(200)

        treeview.append_column(col1)
        treeview.append_column(col2)
        treeview.append_column(col3)

        scroll = Gtk.ScrolledWindow()
        scroll.add(treeview)

        self.add(scroll)


def main():
    win = UpdateWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
