# Changelog

All notable changes to EastLight are documented in this file.

## [0.2.0] — 2026-03-22

### Added

- **PyQt6 graphical interface** — launch with `eastlight gui`
  - Memory list panel: browse all 99 slots with name, track count, and tempo
  - Tabbed memory editor: schema-driven parameter editing for all sections (tracks, master, FX, mixer, routing, EQ, recording, playback, assign, rhythm)
  - System settings editor: SETUP, PREF, MIDI, USB, INPUT, COLOR tabs
  - WAV import/export from the editor
  - Undo/redo for parameter edits
  - Unsaved-changes tracking with confirmation dialogs
  - Device auto-detection and ROLAND/ directory picker
  - Context menu for memory clear operations
- `eastlight gui` CLI command
- `eastlight-gui` script entry point
- CHANGELOG.md

### Known issues

The GUI shipped in 0.2.0 has significant defects found in post-release
review and not yet fixed:

- Clicking a memory that has any FX (input or track effects) crashes
  the editor — `RC0TopLevel` has no `name` attribute, and the FX-tab
  section matching logic doesn't correspond to the real section naming
  scheme.
- Even once the crash is fixed, the Input FX / Track FX tabs cannot
  work as designed and need a redesign around the real subslot/effect
  section structure.
- `Memory` collapses `<ifx>` and `<tfx>` sections into one namespace
  by bare section name; since they share ~1077 identical names, the
  `<tfx>` copy silently wins and `<ifx>` data becomes unreachable
  through `Memory.section()`. This also affects CLI `template-export`
  and `diff`, which only capture/compare the mem-level sections today.
- Undo/redo mutates data directly without notifying listeners, so a
  bound widget can show a stale value after Undo.
- WAV import via the GUI doesn't set track metadata (`has_audio`,
  `total_samples`, etc.) or validate sample rate, unlike the CLI's
  `wav-import` command — imported audio may be silently ignored by the
  device.

Track these as they're fixed in subsequent releases. Recommendation
until then: use the CLI for anything beyond browsing.

## [0.1.0] — 2026-03-22

### Added

- Initial alpha release
- Regex-based RC0 parser with byte-for-byte round-trip fidelity
- ~98% schema coverage (96 YAML schema files)
- 24 CLI commands: memory management, batch operations, audio I/O, FX editing, system settings, MIDI controller assignments, backup management
- 70 effect types fully mapped (66 shared + 4 TFX-exclusive)
- 201 CTL FUNC values mapped with push/hold/click sub-actions
- 47 internal + 6 external controller mapping sections
- Template export/import system (YAML)
- WAV import (WAV/FLAC/OGG with auto-conversion to 32-bit float stereo @ 44.1 kHz)
- WAV export (float32, PCM24, PCM16 formats)
- Automatic timestamped backups before every write
- Dry-run mode on all write commands
- Cross-platform device auto-detection (Linux, macOS, Windows)
- MkDocs documentation site
