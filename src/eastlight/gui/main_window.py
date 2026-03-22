"""Main window for EastLight GUI.

Provides the top-level window with menu bar, memory list,
memory editor, and system settings.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QWidget,
)

from ..core.config import detect_device, load_config, resolve_roland_dir, save_config
from ..core.library import RC505Library
from ..core.schema import SchemaRegistry
from .memory_editor import MemoryEditor
from .memory_list import MemoryListPanel
from .system_editor import SystemEditor


class MainWindow(QMainWindow):
    """EastLight main application window."""

    def __init__(self, roland_dir: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("EastLight - RC-505 MK2 Librarian")
        self.resize(1200, 800)

        self._library: RC505Library | None = None
        self._registry = SchemaRegistry()
        self._registry.load_all()

        # Central widget with placeholder
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Welcome page (shown when no library loaded)
        welcome = QLabel(
            "Welcome to EastLight\n\n"
            "Open a ROLAND/ directory to get started.\n"
            "File → Open ROLAND Directory...\n\n"
            "Or connect your RC-505 MK2 and use File → Detect Device"
        )
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("font-size: 14px; color: #666;")
        self._stack.addWidget(welcome)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._build_menus()
        self._build_toolbar()

        # Try to open a library
        if roland_dir:
            self._open_library(roland_dir)
        else:
            try:
                path = resolve_roland_dir()
                self._open_library(str(path))
            except (ValueError, FileNotFoundError):
                pass

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open ROLAND Directory...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        detect_action = QAction("&Detect Device", self)
        detect_action.triggered.connect(self._on_detect)
        file_menu.addAction(detect_action)

        file_menu.addSeparator()

        # Recent directories
        config = load_config()
        if config.recent:
            for path in config.recent[:5]:
                action = QAction(path, self)
                action.triggered.connect(lambda checked, p=path: self._open_library(p))
                file_menu.addAction(action)
            file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menu_bar.addMenu("&View")

        memories_action = QAction("&Memories", self)
        memories_action.triggered.connect(lambda: self._switch_view("memories"))
        view_menu.addAction(memories_action)

        system_action = QAction("&System Settings", self)
        system_action.triggered.connect(lambda: self._switch_view("system"))
        view_menu.addAction(system_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About EastLight", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction("Memories", lambda: self._switch_view("memories"))
        toolbar.addAction("System", lambda: self._switch_view("system"))
        toolbar.addSeparator()
        toolbar.addAction("Refresh", self._on_refresh)

    def _open_library(self, path: str) -> None:
        """Open a ROLAND/ directory and build the editor UI."""
        try:
            self._library = RC505Library(path)
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        # Update recent list
        config = load_config()
        if path in config.recent:
            config.recent.remove(path)
        config.recent.insert(0, path)
        config.recent = config.recent[:10]
        save_config(config)

        # Build the editor UI
        self._build_editor_ui()
        self._status.showMessage(f"Opened: {path}")
        self.setWindowTitle(f"EastLight - {path}")

    def _build_editor_ui(self) -> None:
        """Build the memory list + editor split view."""
        if self._library is None:
            return

        # Remove old widgets from stack
        while self._stack.count() > 0:
            w = self._stack.widget(0)
            self._stack.removeWidget(w)
            w.deleteLater()

        # Memories view: splitter with list + editor
        memories_widget = QWidget()
        memories_layout = QHBoxLayout(memories_widget)
        memories_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._memory_list = MemoryListPanel(self._library, self._registry)
        self._memory_list.setMinimumWidth(280)
        splitter.addWidget(self._memory_list)

        self._memory_editor = MemoryEditor(self._library, self._registry)
        splitter.addWidget(self._memory_editor)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        memories_layout.addWidget(splitter)

        self._memory_list.memory_selected.connect(self._on_memory_selected)
        self._memory_editor.memory_modified.connect(self._on_memory_modified)

        self._stack.addWidget(memories_widget)

        # System view
        self._system_editor = SystemEditor(self._library, self._registry)
        self._stack.addWidget(self._system_editor)

        self._stack.setCurrentIndex(0)

    def _switch_view(self, view: str) -> None:
        if self._library is None:
            return
        if view == "memories":
            self._stack.setCurrentIndex(0)
        elif view == "system":
            self._stack.setCurrentIndex(1)

    def _on_memory_selected(self, number: int) -> None:
        if hasattr(self, "_memory_editor"):
            if self._memory_editor.has_unsaved_changes():
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "Current memory has unsaved changes. Discard?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            self._memory_editor.load_memory(number)
            self._status.showMessage(f"Memory #{number}")

    def _on_memory_modified(self, number: int) -> None:
        if hasattr(self, "_memory_list"):
            self._memory_list.refresh()
        self._status.showMessage(f"Saved memory #{number}")

    def _on_open(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Select ROLAND Directory",
            "",
        )
        if path:
            self._open_library(path)

    def _on_detect(self) -> None:
        devices = detect_device()
        if not devices:
            QMessageBox.information(self, "Detect", "No RC-505 MK2 devices found.")
            return
        if len(devices) == 1:
            self._open_library(str(devices[0]))
        else:
            # Show list and let user pick
            items = [str(p) for p in devices]
            from PyQt6.QtWidgets import QInputDialog

            item, ok = QInputDialog.getItem(
                self, "Multiple Devices", "Select device:", items, 0, False
            )
            if ok and item:
                self._open_library(item)

    def _on_refresh(self) -> None:
        if self._library is not None:
            self._build_editor_ui()
            self._status.showMessage("Refreshed")

    def _on_about(self) -> None:
        from .. import __version__

        QMessageBox.about(
            self,
            "About EastLight",
            f"EastLight v{__version__}\n\n"
            "Open-source editor/librarian for the\n"
            "Roland RC-505 MK2 loop station.\n\n"
            "License: GPL-3.0-or-later",
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        # Check for unsaved changes
        unsaved = False
        if hasattr(self, "_memory_editor") and self._memory_editor.has_unsaved_changes():
            unsaved = True
        if hasattr(self, "_system_editor") and self._system_editor.has_unsaved_changes():
            unsaved = True

        if unsaved:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "There are unsaved changes. Quit anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

        event.accept()
