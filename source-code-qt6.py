#!/usr/bin/env python3
import subprocess
import re
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer

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
    repo_map = {}
    try:
        output = subprocess.check_output(["pacman", "-Sl"], text=True)
        for line in output.strip().split("\n"):
            if "[" in line and "]" in line:
                parts = line.split()
                if len(parts) >= 2:
                    repo_map[parts[1]] = parts[0]
    except Exception:
        pass
    return repo_map


def get_updates():
    updates = []
    repo_map = get_repo_map()

    # Official repos
    try:
        out_pac = subprocess.check_output(["checkupdates"], text=True)
        for line in out_pac.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                pkg_name = parts[0]
                if pkg_name in repo_map:
                    repo = repo_map[pkg_name]
                    updates.append((pkg_name, parts[1], parts[3], repo))
    except Exception:
        pass

    # AUR via trizen
    try:
        out_aur = subprocess.check_output(["trizen", "-Qu", "--aur"], text=True)
        for line in out_aur.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("::"):
                continue

            parts = line.split()
            if "->" in parts:
                idx = parts.index("->")
                if idx >= 2:
                    pkg_name = parts[idx - 2]
                    old_ver = parts[idx - 1]
                    new_ver = parts[idx + 1]
                    updates.append((pkg_name, old_ver, new_ver, "AUR"))
    except Exception:
        pass

    return updates


class UpdateWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arch & AUR Updates Manager (Qt6)")
        self.setFixedSize(900, 950)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header bar
        header = QHBoxLayout()

        self.refresh_btn = QPushButton("Обнови")
        self.refresh_btn.clicked.connect(self.refresh_updates)
        header.addWidget(self.refresh_btn)

        self.spinner = QProgressBar()
        self.spinner.setRange(0, 0)  # infinite animation
        self.spinner.setVisible(False)
        header.addWidget(self.spinner)

        layout.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Пакет", "Текуща версия", "Нова версия", "Източник"])

        # Fixed column widths
        self.table.setColumnWidth(0, 240)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(2, 240)
        self.table.setColumnWidth(3, 150)

        # Sorting enabled
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)

        # No editing
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        self.refresh_updates()

    def refresh_updates(self):
        self.refresh_btn.setEnabled(False)
        self.spinner.setVisible(True)

        QTimer.singleShot(100, self._load_updates)

    def _load_updates(self):
        self.table.setRowCount(0)

        ignore = read_ignorepkg()
        updates = [u for u in get_updates() if u[0] not in ignore]

        for row, up in enumerate(updates):
            self.table.insertRow(row)
            for col, value in enumerate(up):
                item = QTableWidgetItem(value)
                self.table.setItem(row, col, item)

        self.spinner.setVisible(False)
        self.refresh_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    win = UpdateWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
