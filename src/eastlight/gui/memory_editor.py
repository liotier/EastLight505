"""Memory editor panel for EastLight GUI.

Displays a tabbed view of all sections within a selected memory,
with parameter editors generated from the schema.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.library import RC505Library
from ..core.model import Memory
from ..core.schema import SchemaRegistry
from ..core.wav import import_audio, wav_export, wav_write_device
from .widgets import ScrollableSectionEditor

# Sections to show in tabs, in display order
_SECTION_TABS = [
    ("Tracks", ["TRACK1", "TRACK2", "TRACK3", "TRACK4", "TRACK5", "TRACK6"]),
    ("Master", ["MASTER"]),
    ("Input FX", []),  # Handled specially via FX editor
    ("Track FX", []),  # Handled specially via FX editor
    ("Mixer", ["MIXER"]),
    ("Routing", ["ROUTING"]),
    ("Output", ["OUTPUT"]),
    ("EQ", ["EQ"]),
    ("Recording", ["REC"]),
    ("Playback", ["PLAY"]),
    ("Assign", ["ASSIGN"]),
    ("Rhythm", ["RHYTHM"]),
]


class MemoryEditor(QWidget):
    """Right panel: tabbed editor for a single memory."""

    memory_modified = pyqtSignal(int)  # memory number

    def __init__(
        self,
        library: RC505Library,
        registry: SchemaRegistry,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._registry = registry
        self._memory: Memory | None = None
        self._mem_number: int = 0
        self._dirty = False

        layout = QVBoxLayout(self)

        # Header: memory number + name
        header = QHBoxLayout()
        self._title_label = QLabel("Select a memory")
        self._title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(self._title_label)

        self._name_edit = QLineEdit()
        self._name_edit.setMaxLength(12)
        self._name_edit.setPlaceholderText("Memory name (max 12 chars)")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        self._name_edit.setVisible(False)
        header.addWidget(self._name_edit)

        header.addStretch()

        # Undo/Redo buttons
        self._undo_btn = QPushButton("Undo")
        self._undo_btn.setEnabled(False)
        self._undo_btn.clicked.connect(self._on_undo)
        header.addWidget(self._undo_btn)

        self._redo_btn = QPushButton("Redo")
        self._redo_btn.setEnabled(False)
        self._redo_btn.clicked.connect(self._on_redo)
        header.addWidget(self._redo_btn)

        # Save button
        self._save_btn = QPushButton("Save")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        header.addWidget(self._save_btn)

        layout.addLayout(header)

        # WAV toolbar
        wav_bar = QHBoxLayout()
        self._wav_label = QLabel()
        wav_bar.addWidget(self._wav_label)
        wav_bar.addStretch()
        self._export_btn = QPushButton("Export WAV...")
        self._export_btn.setVisible(False)
        self._export_btn.clicked.connect(self._on_export_wav)
        wav_bar.addWidget(self._export_btn)
        self._import_btn = QPushButton("Import WAV...")
        self._import_btn.setVisible(False)
        self._import_btn.clicked.connect(self._on_import_wav)
        wav_bar.addWidget(self._import_btn)
        layout.addLayout(wav_bar)

        # Tabbed sections
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

    def load_memory(self, number: int) -> None:
        """Load and display a memory slot."""
        try:
            rc0 = self._library.parse_memory(number)
        except FileNotFoundError:
            self._title_label.setText(f"Memory #{number} (empty)")
            self._name_edit.setVisible(False)
            self._tabs.clear()
            self._save_btn.setEnabled(False)
            self._export_btn.setVisible(False)
            self._import_btn.setVisible(False)
            self._wav_label.clear()
            return

        self._memory = Memory(rc0, self._registry)
        self._mem_number = number
        self._dirty = False

        # Header
        name = self._memory.name
        self._title_label.setText(f"Memory #{number}")
        self._name_edit.setText(name)
        self._name_edit.setVisible(True)

        # WAV info
        slot = self._library.memory_slot(number)
        tracks_with_audio = list(slot.wav_paths.keys())
        if tracks_with_audio:
            track_list = ", ".join(str(t) for t in sorted(tracks_with_audio))
            self._wav_label.setText(f"Audio: tracks {track_list}")
        else:
            self._wav_label.setText("No audio")
        self._export_btn.setVisible(bool(tracks_with_audio))
        self._import_btn.setVisible(True)

        # Build section tabs
        self._tabs.clear()
        for tab_name, section_names in _SECTION_TABS:
            if not section_names:
                # FX tabs - build from available FX sections
                sections_for_tab = self._find_fx_sections(tab_name)
                if not sections_for_tab:
                    continue
                tab_widget = self._build_multi_section_tab(sections_for_tab)
            elif len(section_names) == 1:
                section = self._memory.section(section_names[0])
                if section is None:
                    continue
                tab_widget = ScrollableSectionEditor(section)
                tab_widget.editor.param_changed.connect(self._on_param_changed)
            else:
                # Multiple sections (tracks)
                tab_widget = self._build_multi_section_tab(section_names)
            self._tabs.addTab(tab_widget, tab_name)

        self._update_undo_redo()
        self._save_btn.setEnabled(False)

    def _find_fx_sections(self, tab_name: str) -> list[str]:
        """Find FX-related section names for IFX or TFX."""
        if self._memory is None:
            return []
        prefix = "IFX" if "Input" in tab_name else "TFX"
        return [
            name for name in self._memory.section_names
            if name.startswith(prefix) or (
                "_" in name and any(
                    name.startswith(f"{g}{s}_")
                    for g in "ABCD" for s in "ABCD"
                )
                and self._is_fx_section_for(name, prefix)
            )
        ]

    def _is_fx_section_for(self, section_name: str, prefix: str) -> bool:
        """Check if a subslot section belongs to IFX or TFX."""
        if self._memory is None:
            return False
        # IFX sections are those that appear in the IFX element
        # TFX sections appear in the TFX element
        for elem in self._memory.rc0.elements:
            if elem.name and prefix in elem.name and section_name in elem.sections:
                return True
        return False

    def _build_multi_section_tab(self, section_names: list[str]) -> QWidget:
        """Build a tab with sub-tabs for multiple sections."""
        if not section_names:
            return QWidget()

        if self._memory is None:
            return QWidget()

        sub_tabs = QTabWidget()
        for name in section_names:
            section = self._memory.section(name)
            if section is None:
                continue
            editor = ScrollableSectionEditor(section)
            editor.editor.param_changed.connect(self._on_param_changed)
            sub_tabs.addTab(editor, name)
        return sub_tabs

    def _on_name_changed(self) -> None:
        if self._memory is None:
            return
        new_name = self._name_edit.text()
        self._memory.set_name(new_name)
        self._mark_dirty()

    def _on_param_changed(self, section_name: str, param_name: str, value: int) -> None:
        self._mark_dirty()

    def _mark_dirty(self) -> None:
        self._dirty = True
        self._save_btn.setEnabled(True)
        self._update_undo_redo()

    def _update_undo_redo(self) -> None:
        if self._memory:
            self._undo_btn.setEnabled(self._memory.undo_stack.can_undo)
            self._redo_btn.setEnabled(self._memory.undo_stack.can_redo)
        else:
            self._undo_btn.setEnabled(False)
            self._redo_btn.setEnabled(False)

    def _on_undo(self) -> None:
        if self._memory:
            self._memory.undo()
            self._update_undo_redo()

    def _on_redo(self) -> None:
        if self._memory:
            self._memory.redo()
            self._update_undo_redo()

    def _on_save(self) -> None:
        if self._memory is None:
            return
        try:
            self._library.save_memory(self._mem_number, self._memory.rc0)
            self._dirty = False
            self._save_btn.setEnabled(False)
            self.memory_modified.emit(self._mem_number)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _on_export_wav(self) -> None:
        if self._memory is None:
            return
        slot = self._library.memory_slot(self._mem_number)
        tracks = sorted(slot.wav_paths.keys())
        if not tracks:
            return

        # For simplicity, export first available track
        track = tracks[0]
        wav_path = slot.track_wav(track)
        if wav_path is None:
            return

        dest, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Track {track}",
            f"memory{self._mem_number:03d}_track{track}.wav",
            "WAV files (*.wav)",
        )
        if dest:
            try:
                import soundfile as sf
                data, sr = sf.read(str(wav_path), dtype="float32")
                wav_export(dest, data, sr)
                QMessageBox.information(self, "Export", f"Exported track {track} to {dest}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _on_import_wav(self) -> None:
        if self._memory is None:
            return

        src, _ = QFileDialog.getOpenFileName(
            self,
            "Import Audio",
            "",
            "Audio files (*.wav *.flac *.ogg)",
        )
        if not src:
            return

        # Import to track 1 by default
        track = 1
        wav_dir = self._library.wave_dir / f"{self._mem_number:03d}_{track}"
        wav_dir.mkdir(parents=True, exist_ok=True)
        dest = wav_dir / f"{self._mem_number:03d}_{track}.WAV"

        try:
            data, sr = import_audio(src)
            wav_write_device(str(dest), data, sr)
            QMessageBox.information(self, "Import", f"Imported to track {track}")
            self.load_memory(self._mem_number)  # Refresh
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))

    def has_unsaved_changes(self) -> bool:
        return self._dirty
