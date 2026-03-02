#!/usr/bin/env python3
import subprocess
import re
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QMainWindow
from PyQt6.QtCore import Qt

PACMAN_CONF = "/etc/pacman.conf"


def read_ignorepkg():
    ignore = set()
    pattern = re.compile(r"^\s*IgnorePkg\s*=\s*(.*)$")
    with open(PACMAN_CONF, "r") as f:
        for line in f:
            m = pattern.match(line)
            if m:
                ignore.update(m.group(1).split())
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
        parts = line.split()
        if len(parts) >= 4 and parts[2] == "->":
            updates.append((parts[0], parts[1], parts[3]))
    return updates


class UpdateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arch Updates QT6")
        self.resize(700, 600)

        ignore = read_ignorepkg()
        updates = [u for u in get_updates() if u[0] not in ignore]

        table = QTableWidget(len(updates), 3)
        table.setHorizontalHeaderLabels(["Package name", "Current version", "New version"])
        table.setColumnWidth(0, 300)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 200)

        for row, (pkg, old, new) in enumerate(updates):
            table.setItem(row, 0, QTableWidgetItem(pkg))
            table.setItem(row, 1, QTableWidgetItem(old))
            table.setItem(row, 2, QTableWidgetItem(new))

        self.setCentralWidget(table)


app = QApplication([])
win = UpdateWindow()
win.show()
app.exec()
