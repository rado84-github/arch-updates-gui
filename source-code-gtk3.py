#!/usr/bin/env python3
import gi
import subprocess
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

PACMAN_CONF = "/etc/pacman.conf"

def read_ignorepkg():
    ignore = set()
    pattern = re.compile(r"^\s*IgnorePkg\s*=\s*([^#]*)")
    try:
        with open(PACMAN_CONF, "r") as f:
            for line in f:
                m = pattern.match(line)
                if m:
                    pkgs = m.group(1).split()
                    ignore.update(pkgs)
    except FileNotFoundError:
        pass
    return ignore

def get_repo_map():
    """Създава речник САМО за инсталираните пакети от официалните хранилища."""
    repo_map = {}
    try:
        # pacman -Sl извежда: repo_name pkg_name version [installed]
        output = subprocess.check_output(["pacman", "-Sl"], text=True)
        for line in output.strip().split("\n"):
            # Проверяваме дали редът съдържа квадратни скоби (индикация за инсталиран пакет)
            if "[" in line and "]" in line:
                parts = line.split()
                if len(parts) >= 2:
                    # parts[0] е името на хранилището (core, extra, multilib)
                    # parts[1] е името на пакета
                    repo_map[parts[1]] = parts[0]
    except Exception:
        pass
    return repo_map

def get_updates():
    updates = []
    repo_map = get_repo_map()

    # 1. Официални ъпдейти (само ако са в repo_map)
    try:
        out_pac = subprocess.check_output(["checkupdates"], text=True)
        for line in out_pac.strip().split("\n"):
            if not line.strip(): continue
            parts = line.split()
            if len(parts) >= 4:
                pkg_name = parts[0]
                # ПРОВЕРКА: Показваме пакета само ако е намерен в официалните хранилища
                if pkg_name in repo_map:
                    repo = repo_map[pkg_name]
                    updates.append((pkg_name, parts[1], parts[3], repo))
                # Ако го няма в repo_map, скриптът просто не го добавя (игнорира го)
    except Exception:
        pass

    # 2. AUR ъпдейти чрез trizen
    try:
        # Използваме командата, която ти даде най-добър резултат
        out_aur = subprocess.check_output(["trizen", "-Qu", "--aur"], text=True)
        
        for line in out_aur.strip().split("\n"):
            line = line.strip()
            # Филтрираме: пропускаме редове, които започват с "::" или са празни
            if not line or line.startswith("::"):
                continue
                
            parts = line.split()
            # Търсим само редове от типа: име версия -> версия
            # (обикновено са точно 4 части)
            if "->" in parts:
                idx = parts.index("->")
                if idx >= 2: # Трябва да имаме име и стара версия преди ->
                    pkg_name = parts[idx-2]
                    old_ver = parts[idx-1]
                    new_ver = parts[idx+1]
                    updates.append((pkg_name, old_ver, new_ver, "AUR"))
    except Exception:
        # trizen връща грешка, ако няма AUR ъпдейти, затова просто прескачаме
        pass

    return updates

class UpdateWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Arch & AUR Updates Manager")
        self.set_default_size(900, 950) # (width, height)
        self.set_resizable(False)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)

        # Toolbar-like Header
        self.header_box = Gtk.Box(spacing=10)
        self.header_box.set_margin_top(10)
        self.header_box.set_margin_bottom(10)
        self.header_box.set_margin_start(10)
        self.header_box.set_margin_end(10)
        
        self.refresh_btn = Gtk.Button(label="Обнови")
        self.refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header_box.pack_start(self.refresh_btn, False, False, 0)
        
        self.spinner = Gtk.Spinner()
        self.header_box.pack_start(self.spinner, False, False, 0)
        
        self.main_box.pack_start(self.header_box, False, False, 0)

        # TreeView
        self.liststore = Gtk.ListStore(str, str, str, str)
        self.liststore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.treeview = Gtk.TreeView(model=self.liststore)
        
        columns = ["Пакет", "Текуща версия", "Нова версия", "Източник"]
        for i, title in enumerate(columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_sort_column_id(i)
            column.set_resizable(True)
            
            # Настройки за ширината:
            if i == 0:  # Това е колоната "Пакет"
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_fixed_width(240)
            if i == 1:  # Това е колоната "Текуща версия"
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_fixed_width(240)
            if i == 2:  # Това е колоната "Нова версия"
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_fixed_width(240)
            if i == 3:  # Това е колоната "Хранилище"
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_fixed_width(150)

            self.treeview.append_column(column)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add(self.treeview)
        self.main_box.pack_start(self.scroll, True, True, 0)

        self.refresh_updates()

    def refresh_updates(self):
        self.liststore.clear()
        self.refresh_btn.set_sensitive(False)
        self.spinner.start()
        
        # Обновяваме данните
        ignore = read_ignorepkg()
        updates = [u for u in get_updates() if u[0] not in ignore]
        
        for up in updates:
            self.liststore.append(list(up))
            
        self.spinner.stop()
        self.refresh_btn.set_sensitive(True)

    def on_refresh_clicked(self, widget):
        self.refresh_updates()

def main():
    win = UpdateWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
