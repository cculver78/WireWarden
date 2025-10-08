"""

PyQt6 WireGuard Manager

- On startup, checks all *.conf files in the folder.
- If any contain spaces or invalid characters (not matching WireGuard's valid pattern [A-Za-z0-9_=+.-]), shows an error dialog listing them and disables controls until fixed.

- Centered name labels.
- UP/DOWN buttons; only the opposite of current state is clickable.
- Single connection enforcement (must disconnect before bringing up another).
- Window auto-sizes to fit all visible cards.

"""

from __future__ import annotations
import os
import re
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Dict, Set

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame,
)

APP_POLL_MS = 3000
VALID_IFACE_PATTERN = re.compile(r'^[A-Za-z0-9_=+.-]+$')

GREEN = "#1b5e20"
GREEN_HOVER = "#1f6b24"
GREEN_PRESS = "#17521d"
RED = "#b71c1c"
RED_HOVER = "#c31f1f"
RED_PRESS = "#9f1818"
NEUTRAL = "#2b2f36"
NEUTRAL_HOVER = "#313640"
NEUTRAL_PRESS = "#272b33"

BTN_BASE = (
    "QPushButton { background-color: %s; color: #e0e0e0; border: 1px solid #222; border-radius: 8px; padding: 8px 12px; }\n"
    "QPushButton:hover { background-color: %s; }\n"
    "QPushButton:pressed { background-color: %s; }\n"
)

class IfaceCard(QFrame):
    def __init__(self, name: str, on_up, on_down):
        super().__init__()
        self.name = name
        self.on_up = on_up
        self.on_down = on_down

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("ifaceCard")
        self.setStyleSheet(
            """
            QFrame#ifaceCard { background-color: #15191e; border: 1px solid #222; border-radius: 10px; }
            QLabel.title { color: #e8e8e8; font-weight: 700; font-size: 16px; }
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 12)
        outer.setSpacing(8)

        # Centered name label
        title = QLabel(name)
        title.setObjectName("title")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        outer.addWidget(title)

        # Two-button row (no big toggle)
        row = QHBoxLayout()
        self.up_btn = QPushButton("UP")
        self.down_btn = QPushButton("DOWN")
        self.up_btn.clicked.connect(lambda _=False: self.on_up(self.name))
        self.down_btn.clicked.connect(lambda _=False: self.on_down(self.name))
        row.addWidget(self.up_btn)
        row.addWidget(self.down_btn)
        outer.addLayout(row)

    def set_state(self, is_up: bool):
        if is_up:
            self.up_btn.setEnabled(False)
            self.down_btn.setEnabled(True)
            self.up_btn.setStyleSheet(BTN_BASE % (GREEN, GREEN_HOVER, GREEN_PRESS))
            self.down_btn.setStyleSheet(BTN_BASE % (NEUTRAL, NEUTRAL_HOVER, NEUTRAL_PRESS))
        else:
            self.up_btn.setEnabled(True)
            self.down_btn.setEnabled(False)
            self.up_btn.setStyleSheet(BTN_BASE % (NEUTRAL, NEUTRAL_HOVER, NEUTRAL_PRESS))
            self.down_btn.setStyleSheet(BTN_BASE % (RED, RED_HOVER, RED_PRESS))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WireWarden")
        self.app_dir = Path(__file__).parent.resolve()

        outer = QWidget()
        self.outer_layout = QVBoxLayout(outer)
        self.outer_layout.setContentsMargins(12, 12, 12, 12)
        self.outer_layout.setSpacing(10)

        header_row = QHBoxLayout()
        hdr = QLabel("Interfaces in this folder:")
        header_row.addWidget(hdr)
        header_row.addStretch(1)
        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet("color: #888;")
        header_row.addWidget(self.status_label)
        self.outer_layout.addLayout(header_row)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.outer_layout.addWidget(self.cards_container)

        self.setCentralWidget(outer)

        self.cards: Dict[str, IfaceCard] = {}

        invalid_files = self.check_invalid_configs()
        if invalid_files:
            msg = ("The following config files have invalid names and cannot be used by WireGuard:\n\n" +
                   "\n".join(invalid_files) +
                   "\n\nFile names must only contain letters, numbers, '+', '-', '_', '=', or '.' and have no spaces.")
            QMessageBox.critical(self, "Invalid Config Filenames", msg)
        else:
            self.load_configs()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(APP_POLL_MS)
        self.refresh()
        self.adjust_to_content()

    def check_invalid_configs(self) -> list[str]:
        invalid = []
        for path in sorted(self.app_dir.glob("*.conf")):
            if not VALID_IFACE_PATTERN.match(path.stem):
                invalid.append(path.name)
        return invalid

    def load_configs(self) -> None:
        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if w is not None:
                w.setParent(None)
        self.cards.clear()

        for path in sorted(self.app_dir.glob("*.conf")):
            name = path.stem
            if not VALID_IFACE_PATTERN.match(name):
                continue
            card = IfaceCard(name, self.bring_up, self.bring_down)
            self.cards_layout.addWidget(card)
            self.cards[name] = card

        self.cards_layout.addStretch(1)

    def get_active_ifaces(self) -> Set[str]:
        try:
            result = subprocess.run(["wg", "show", "interfaces"], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                return set()
            return set(result.stdout.strip().split())
        except FileNotFoundError:
            return set()

    def refresh(self) -> None:
        active = self.get_active_ifaces()
        for name, card in self.cards.items():
            card.set_state(name in active)
        self.status_label.setText("Active: " + (", ".join(sorted(active)) if active else "none"))
        self.adjust_to_content()

    def adjust_to_content(self) -> None:
        self.layout().activate()
        self.adjustSize()
        sz = self.sizeHint()
        self.setFixedSize(max(520, sz.width()+10), sz.height()+10)

    def bring_up(self, name: str) -> None:
        active = self.get_active_ifaces()
        if active and (name not in active):
            QMessageBox.warning(self, "Disconnect first", f"Another WireGuard interface is active: {', '.join(sorted(active))}.\nDisconnect it before bringing up {name}.")
            return
        if name in active:
            return
        self.run_wg_quick(name, up=True)

    def bring_down(self, name: str) -> None:
        active = self.get_active_ifaces()
        if name not in active:
            return
        self.run_wg_quick(name, up=False)

    def run_wg_quick(self, name: str, up: bool) -> None:
        conf_path = self.app_dir / f"{name}.conf"
        if not conf_path.exists():
            QMessageBox.critical(self, "Error", f"Config not found: {conf_path}")
            return

        cmd = ["wg-quick", "up" if up else "down", str(conf_path)]

        needs_elev = os.geteuid() != 0
        pkexec = shutil.which("pkexec")
        if needs_elev and pkexec:
            cmd = [pkexec] + cmd

        try:
            self.status_label.setText("Running: " + " ".join(cmd))
            proc = subprocess.run(cmd, cwd=self.app_dir, capture_output=True, text=True)
        except Exception as e:
            QMessageBox.critical(self, "Execution failed", str(e))
            return

        if proc.returncode != 0:
            msg = proc.stderr.strip() or proc.stdout.strip() or "wg-quick failed"
            QMessageBox.warning(self, "wg-quick error", msg)
        self.refresh()


def main() -> int:
    app = QApplication(sys.argv)

    app.setStyleSheet(
        f"""
        QWidget {{ font-family: Sans-Serif; font-size: 14px; }}
        QMainWindow {{ background-color: #111417; }}
        QLabel {{ color: #e0e0e0; }}
        QPushButton {{ background-color: {NEUTRAL}; color: #e0e0e0; border: 1px solid #222; border-radius: 8px; padding: 8px 12px; }}
        QPushButton:hover {{ background-color: {NEUTRAL_HOVER}; }}
        QPushButton:pressed {{ background-color: {NEUTRAL_PRESS}; }}
        QMessageBox {{ background-color: #111417; }}
        QFrame#ifaceCard {{ background-color: #15191e; border: 1px solid #222; border-radius: 10px; }}
        QLabel.title {{ color: #e8e8e8; font-weight: 700; font-size: 16px; }}
        """
    )

    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
