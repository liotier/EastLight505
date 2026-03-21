"""Memory list panel for EastLight GUI.

Displays all 99 memory slots in a table with name, track count,
tempo, and audio status. Supports selection, context menu for
copy/swap/clear operations.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.library import RC505Library
from ..core.model import Memory
from ..core.schema import SchemaRegistry


class MemoryListPanel(QWidget):
    """Left panel showing all 99 memory slots."""

    memory_selected = pyqtSignal(int)  # memory number (1-99)

    def __init__(
        self,
        library: RC505Library,
        registry: SchemaRegistry,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._registry = registry

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["#", "Name", "Tracks", "Tempo"])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._context_menu)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self._table.cellClicked.connect(self._on_click)
        layout.addWidget(self._table)

        self.refresh()

    def refresh(self) -> None:
        """Reload all memory slots from the library."""
        self._table.setRowCount(99)

        for i in range(1, 100):
            row = i - 1
            slot = self._library.memory_slot(i)

            # Number
            num_item = QTableWidgetItem(str(i))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, num_item)

            # Name
            name = ""
            if slot.exists:
                try:
                    name = self._library.memory_name(i)
                except Exception:
                    name = "(error)"
            self._table.setItem(row, 1, QTableWidgetItem(name))

            # Track count (how many WAV files)
            track_count = len(slot.wav_paths)
            tracks_text = str(track_count) if track_count > 0 else ""
            tracks_item = QTableWidgetItem(tracks_text)
            tracks_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, tracks_item)

            # Tempo
            tempo_text = ""
            if slot.exists:
                try:
                    rc0 = self._library.parse_memory(i)
                    mem = Memory(rc0, self._registry)
                    master = mem.section("MASTER")
                    if master:
                        tempo_raw = master.get_by_name("tempo_x10")
                        if tempo_raw is not None and tempo_raw > 0:
                            tempo_text = f"{tempo_raw / 10:.1f}"
                except Exception:
                    pass
            tempo_item = QTableWidgetItem(tempo_text)
            tempo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, tempo_item)

    def _on_click(self, row: int, _col: int) -> None:
        self.memory_selected.emit(row + 1)

    def _context_menu(self, pos) -> None:
        row = self._table.rowAt(pos.y())
        if row < 0:
            return

        mem_num = row + 1
        menu = QMenu(self)

        menu.addAction(f"Copy #{mem_num}...")
        menu.addAction(f"Swap #{mem_num}...")
        menu.addSeparator()
        clear_action = menu.addAction(f"Clear #{mem_num}")

        action = menu.exec(self._table.viewport().mapToGlobal(pos))

        if action == clear_action:
            reply = QMessageBox.question(
                self,
                "Clear Memory",
                f"Clear memory #{mem_num}? A backup will be created.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self._library.clear_memory(mem_num)
                    self.refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
