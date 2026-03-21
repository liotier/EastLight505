# Development

## Setup

```bash
git clone https://github.com/liotier/EastLightRC-505mk2Librarian.git
cd EastLightRC-505mk2Librarian
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
pytest --tb=short -q            # Compact output
pytest -k "test_parser"         # Run specific tests
```

## Linting

```bash
ruff check src/ tests/
ruff format src/ tests/         # Auto-format
```

## Architecture

```
src/eastlight/
  core/
    parser.py      Regex-based RC0 reader (handles Roland's non-standard XML)
    writer.py      RC0 serializer (byte-for-byte roundtrip fidelity)
    model.py       Typed data model with undo/redo and change observers
    schema.py      YAML-driven parameter mapping with FX suffix matching
    library.py     ROLAND/ directory operations with auto-backup
    wav.py         32-bit float WAV import/export via libsndfile
    config.py      User config, device auto-detection, dir resolution
  schema/
    *.yaml         24 section schemas + ctl_func enum (201 entries)
    effects/       70 FX effect type schemas
    fx_types.yaml  FX type index enum (IFX 0-65, TFX 0-69)
    ctl_func.yaml  CTL FUNC enum (0-200) with sub-actions
  cli/
    main.py        Click-based CLI (25 commands)
  gui/
    __init__.py    Application launcher
    main_window.py Main window with menu bar, toolbar, split view
    memory_list.py Memory slot browser (99 slots)
    memory_editor.py Tabbed parameter editor per memory
    system_editor.py System settings editor
    widgets.py     Schema-driven parameter controls (spinbox, combo, checkbox)
```

## Design principles

- **Schema-driven**: YAML files define parameter mappings. Adding or fixing mappings means editing YAML, not code.
- **Round-trip fidelity**: Parser and writer produce byte-identical output. No data is lost or reformatted.
- **Core library with no UI dependencies**: `eastlight.core` supports scripting, CLI, and GUI equally.
- **Safety first**: Automatic backups before every write. Dry-run mode on all write commands.

## Release process

1. Update version in `pyproject.toml`
2. Commit and push to `main`
3. Create a GitHub release with a tag like `v0.1.0`
4. GitHub Actions automatically builds and publishes to PyPI
5. GitHub Pages documentation is updated on every push to `main`
