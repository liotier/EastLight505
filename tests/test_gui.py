"""Smoke tests for the EastLight GUI module.

Tests cover module imports, widget construction logic, and the launch
function's PyQt6 dependency check. Qt widget tests are skipped if
PyQt6 is not installed or no display is available.
"""

from __future__ import annotations

import pytest

# --- Import tests (no PyQt6 required) ---


def test_gui_launch_function_exists():
    """The gui module exposes a launch() function."""
    from eastlight.gui import launch

    assert callable(launch)


def test_gui_launch_without_pyqt6(monkeypatch):
    """launch() raises SystemExit with helpful message when PyQt6 is missing."""
    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "PyQt6.QtWidgets":
            raise ImportError("No module named 'PyQt6'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    from eastlight.gui import launch

    with pytest.raises(SystemExit, match="PyQt6 is required"):
        launch()


def test_gui_cli_command_registered():
    """The 'gui' command is registered in the CLI group."""
    from eastlight.cli.main import cli

    command_names = [cmd for cmd in cli.commands]
    assert "gui" in command_names


# --- Schema-driven widget logic tests (no Qt required) ---


def test_section_tabs_defined():
    """Memory editor defines section tabs for the UI."""
    # Import just the constant, not the Qt-dependent classes
    import ast
    from pathlib import Path

    gui_dir = Path(__file__).parent.parent / "src" / "eastlight" / "gui"
    source = (gui_dir / "memory_editor.py").read_text()
    tree = ast.parse(source)

    # Find the _SECTION_TABS assignment
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_SECTION_TABS":
                    found = True
    assert found, "_SECTION_TABS constant not found in memory_editor.py"


def test_system_tabs_defined():
    """System editor defines system tabs for the UI."""
    import ast
    from pathlib import Path

    gui_dir = Path(__file__).parent.parent / "src" / "eastlight" / "gui"
    source = (gui_dir / "system_editor.py").read_text()
    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_SYSTEM_TABS":
                    found = True
    assert found, "_SYSTEM_TABS constant not found in system_editor.py"


def test_all_gui_modules_parse():
    """All GUI Python files parse without syntax errors."""
    import ast
    from pathlib import Path

    gui_dir = Path(__file__).parent.parent / "src" / "eastlight" / "gui"
    py_files = list(gui_dir.glob("*.py"))
    assert len(py_files) >= 6, f"Expected at least 6 GUI modules, found {len(py_files)}"

    for py_file in py_files:
        ast.parse(py_file.read_text(), filename=str(py_file))


# --- PyQt6-dependent tests (skipped if not available) ---

try:
    from PyQt6.QtWidgets import QApplication

    _has_pyqt6 = True
except ImportError:
    _has_pyqt6 = False

# Check for a usable Qt platform: a real display, an explicitly requested
# headless plugin (QT_QPA_PLATFORM=offscreen and friends), or any non-Linux
# OS (Windows/macOS always have a window server, so DISPLAY is irrelevant).
_has_display = False
if _has_pyqt6:
    import os
    import sys

    _has_display = (
        sys.platform != "linux"
        or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
        or os.environ.get("QT_QPA_PLATFORM") in {"offscreen", "minimal", "vnc"}
    )

requires_qt = pytest.mark.skipif(
    not (_has_pyqt6 and _has_display),
    reason="PyQt6 not installed or no usable Qt platform",
)


@requires_qt
class TestWidgets:
    """Tests that require PyQt6 and a display."""

    @pytest.fixture(autouse=True)
    def qt_app(self):
        """Ensure a QApplication exists for widget tests."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app

    def test_param_widget_bool(self):
        from eastlight.core.schema import FieldDef
        from eastlight.gui.widgets import ParamWidget

        fd = FieldDef(tag="A", name="reverse", type="bool", display="Reverse")
        widget = ParamWidget(fd, current_value=0)
        assert widget is not None

    def test_param_widget_enum(self):
        from eastlight.core.schema import FieldDef
        from eastlight.gui.widgets import ParamWidget

        fd = FieldDef(
            tag="E",
            name="start_mode",
            type="enum",
            display="Start",
            choices={0: "IMMEDIATE", 1: "FADE IN"},
        )
        widget = ParamWidget(fd, current_value=0)
        assert widget is not None

    def test_param_widget_int(self):
        from eastlight.core.schema import FieldDef
        from eastlight.gui.widgets import ParamWidget

        fd = FieldDef(
            tag="C", name="pan", type="int", display="Pan", range=(0, 100)
        )
        widget = ParamWidget(fd, current_value=50)
        assert widget is not None

    def test_param_widget_set_value(self):
        from eastlight.core.schema import FieldDef
        from eastlight.gui.widgets import ParamWidget

        fd = FieldDef(
            tag="D", name="play_level", type="int", display="Play Level", range=(0, 200)
        )
        widget = ParamWidget(fd, current_value=100)
        widget.set_value(150)
        # Should not crash

    def test_param_widget_readonly(self):
        from eastlight.core.schema import FieldDef
        from eastlight.gui.widgets import ParamWidget

        fd = FieldDef(
            tag="W", name="has_audio", type="bool", display="Has Audio", read_only=True
        )
        widget = ParamWidget(fd, current_value=0)
        assert not widget._control.isEnabled()

    def test_section_editor_creates(self):
        from eastlight.core.model import ResolvedSection
        from eastlight.core.parser import RC0Section
        from eastlight.core.schema import FieldDef, SectionSchema
        from eastlight.gui.widgets import SectionEditor

        fd = FieldDef(
            tag="A", name="test_param", type="int",
            display="Test", range=(0, 100),
        )
        schema = SectionSchema(
            section="TEST",
            instances=["TEST1"],
            fields={"A": fd},
        )
        raw = RC0Section(name="TEST1", fields={"A": 50})
        resolved = ResolvedSection(raw=raw, schema=schema)
        editor = SectionEditor(resolved)
        assert editor is not None
