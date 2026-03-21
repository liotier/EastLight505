"""System settings editor for EastLight GUI.

Displays system-level settings (SETUP, PREF, MIDI, USB, etc.)
in a tabbed layout with schema-aware parameter editors.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.library import RC505Library
from ..core.model import Memory
from ..core.schema import SchemaRegistry
from .widgets import ScrollableSectionEditor

# System sections to display, grouped into tabs
_SYSTEM_TABS = [
    ("Setup", ["SETUP"]),
    ("Preferences", ["PREF"]),
    ("MIDI", ["MIDI"]),
    ("USB", ["USB"]),
    ("Input", ["INPUT"]),
    ("Color", ["COLOR"]),
]


class SystemEditor(QWidget):
    """Editor for system-level (SYSTEM1.RC0) settings."""

    def __init__(
        self,
        library: RC505Library,
        registry: SchemaRegistry,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._registry = registry
        self._system: Memory | None = None
        self._dirty = False

        layout = QVBoxLayout(self)

        title = QLabel("System Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self._save_btn = QPushButton("Save System Settings")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._load()

    def _load(self) -> None:
        try:
            rc0 = self._library.parse_system()
            self._system = Memory(rc0, self._registry)
        except Exception:
            self._tabs.addTab(QLabel("Could not load system settings"), "Error")
            return

        for tab_name, section_names in _SYSTEM_TABS:
            for name in section_names:
                section = self._system.section(name)
                if section is None:
                    continue
                editor = ScrollableSectionEditor(section)
                editor.editor.param_changed.connect(self._on_param_changed)
                self._tabs.addTab(editor, tab_name)

    def _on_param_changed(self, section_name: str, param_name: str, value: int) -> None:
        self._dirty = True
        self._save_btn.setEnabled(True)

    def _on_save(self) -> None:
        if self._system is None:
            return
        try:
            self._library.save_system(self._system.rc0)
            self._dirty = False
            self._save_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def has_unsaved_changes(self) -> bool:
        return self._dirty
