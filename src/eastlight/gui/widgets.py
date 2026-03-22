"""Reusable parameter editor widgets for EastLight GUI.

Provides schema-aware widgets that automatically render the correct
control type (spinbox, combo, checkbox) based on FieldDef metadata.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QWidget,
)

from ..core.model import FieldChange, ResolvedSection
from ..core.schema import FieldDef


class ParamWidget(QWidget):
    """A single parameter editor: label + appropriate control.

    Emits value_changed(param_name, new_value) when the user edits.
    """

    value_changed = pyqtSignal(str, int)

    def __init__(
        self, field_def: FieldDef, current_value: int, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._field_def = field_def
        self._updating = False  # Guard against feedback loops

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if field_def.type == "bool":
            self._control = self._make_checkbox(current_value)
        elif field_def.type == "enum" and field_def.choices:
            self._control = self._make_combo(field_def.choices, current_value)
        else:
            self._control = self._make_spinbox(field_def, current_value)

        layout.addWidget(self._control)

        if field_def.unit:
            layout.addWidget(QLabel(field_def.unit))

        if field_def.read_only or field_def.computed:
            self._control.setEnabled(False)

    def _make_checkbox(self, value: int) -> QCheckBox:
        cb = QCheckBox()
        cb.setChecked(bool(value))
        cb.checkStateChanged.connect(self._on_checkbox)
        return cb

    def _make_combo(self, choices: dict[int, str], value: int) -> QComboBox:
        combo = QComboBox()
        self._combo_keys: list[int] = []
        for k, v in sorted(choices.items()):
            combo.addItem(v, k)
            self._combo_keys.append(k)
        idx = self._combo_keys.index(value) if value in self._combo_keys else 0
        combo.setCurrentIndex(idx)
        combo.currentIndexChanged.connect(self._on_combo)
        return combo

    def _make_spinbox(self, fd: FieldDef, value: int) -> QSpinBox:
        spin = QSpinBox()
        if fd.range:
            spin.setMinimum(fd.range[0])
            spin.setMaximum(fd.range[1])
        else:
            spin.setMinimum(0)
            spin.setMaximum(999999999)
        spin.setValue(value)
        spin.valueChanged.connect(self._on_spin)
        return spin

    def _on_checkbox(self) -> None:
        if not self._updating:
            val = 1 if self._control.isChecked() else 0
            self.value_changed.emit(self._field_def.name, val)

    def _on_combo(self, index: int) -> None:
        if not self._updating and 0 <= index < len(self._combo_keys):
            self.value_changed.emit(self._field_def.name, self._combo_keys[index])

    def _on_spin(self, value: int) -> None:
        if not self._updating:
            self.value_changed.emit(self._field_def.name, value)

    def set_value(self, value: int) -> None:
        """Programmatically update the displayed value without emitting signals."""
        self._updating = True
        try:
            if isinstance(self._control, QCheckBox):
                self._control.setChecked(bool(value))
            elif isinstance(self._control, QComboBox):
                idx = self._combo_keys.index(value) if value in self._combo_keys else 0
                self._control.setCurrentIndex(idx)
            elif isinstance(self._control, QSpinBox):
                self._control.setValue(value)
        finally:
            self._updating = False


class SectionEditor(QGroupBox):
    """Editor panel for a single section (e.g., TRACK1, MASTER).

    Displays all editable fields from the section's schema as a form.
    """

    param_changed = pyqtSignal(str, str, int)  # section_name, param_name, value

    def __init__(
        self,
        section: ResolvedSection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(section.raw.name, parent)
        self._section = section
        self._widgets: dict[str, ParamWidget] = {}

        form = QFormLayout()
        self.setLayout(form)

        if section.schema is None:
            form.addRow(QLabel("(no schema available)"))
            return

        for tag, fd in section.schema.fields.items():
            value = section.get_by_tag(tag)
            widget = ParamWidget(fd, value)
            widget.value_changed.connect(self._on_value_changed)
            self._widgets[fd.name] = widget
            form.addRow(fd.display + ":", widget)

        # Listen for external changes (undo/redo, other editors)
        section.add_listener(self._on_external_change)

    def _on_value_changed(self, param_name: str, value: int) -> None:
        try:
            self._section.set_by_name(param_name, value)
            self.param_changed.emit(self._section.raw.name, param_name, value)
        except (ValueError, KeyError):
            # Revert widget to current value
            current = self._section.get_by_name(param_name)
            if current is not None and param_name in self._widgets:
                self._widgets[param_name].set_value(current)

    def _on_external_change(self, change: FieldChange) -> None:
        if change.param_name and change.param_name in self._widgets:
            self._widgets[change.param_name].set_value(change.new_value)


class ScrollableSectionEditor(QScrollArea):
    """A scrollable wrapper around a SectionEditor."""

    def __init__(
        self, section: ResolvedSection, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._editor = SectionEditor(section)
        self.setWidget(self._editor)
        self.setWidgetResizable(True)

    @property
    def editor(self) -> SectionEditor:
        return self._editor
