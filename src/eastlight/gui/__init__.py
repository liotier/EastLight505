"""GUI interface for EastLight (PyQt6).

Provides a graphical editor/librarian for the Roland RC-505 MK2.
"""


def launch(roland_dir: str | None = None) -> int:
    """Launch the EastLight GUI application.

    Args:
        roland_dir: Optional path to ROLAND/ directory. If None,
            uses config or auto-detection.

    Returns:
        Application exit code.
    """
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        raise SystemExit(
            "PyQt6 is required for the GUI.\n"
            "Install it with: pip install eastlight[gui]"
        ) from None

    import sys

    from .main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("EastLight")
    app.setOrganizationName("EastLight")

    window = MainWindow(roland_dir=roland_dir)
    window.show()

    return app.exec()
