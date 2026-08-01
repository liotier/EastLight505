# Changelog

All notable changes to EastLight are documented in this file.

## [Unreleased]

### Fixed

- **`Memory` no longer collapses `<ifx>`/`<tfx>` sections into one
  namespace.** Both chains share ~1000 identical section names (`AA`,
  `AA_LPF`, ...); the previous flat, bare-name-keyed dict let `<tfx>`
  silently overwrite `<ifx>`, making input-FX data unreachable through
  `Memory.section()`. Added `Memory.fx_section(chain, name)` and
  `fx_section_names(chain)` as the correct accessors. As a side effect,
  this also stopped the GUI from crashing on any memory with FX
  sections (`RC0TopLevel` has no `name` attribute — the crash's
  trigger path is no longer reachable). The FX/EQ/ASSIGN tabs
  themselves are still not implemented in the GUI.
- **`template-export`/`template-apply`/`diff` now cover IFX and TFX.**
  Previously they iterated only `Memory.section_names`, which (due to
  the collision above) silently omitted input-FX data from templates
  and could report two memories as identical when they only differed
  in IFX settings. Templates now have `_ifx_sections`/`_tfx_sections`
  blocks alongside `_sections`; old-format templates (mem-only) still
  apply correctly.
- **`Memory.undo()`/`redo()` now notify listeners.** They previously
  mutated the underlying data directly to avoid re-pushing onto the
  undo stack, which meant any bound observer (e.g. a GUI widget) never
  heard about the reversal and could display a stale value. Added
  `ResolvedSection._apply_silent()` to notify without re-pushing.
- **Extracted `core.operations.import_track_audio()`** as the single
  source of truth for importing audio into a track (sample-rate
  validation, writing the WAV, updating `has_audio`/`total_samples`/
  `samples_per_measure`/`loop_length`). The CLI's `wav-import` now
  calls this instead of its own inline copy of the logic; the GUI's
  own (incomplete) copy is unchanged pending the GUI fix pass this
  depends on.
- Clarified in `Memory.track()`'s docstring that TRACK6 exists in
  every real memory file but is not user-accessible on the RC-505 mk2
  (likely a holdover from the shared RC-505mk2/RC-600 codebase).
- Fixed all 35 pre-existing `ruff` lint violations (the CI lint gate
  had been red since the workflow was created — none were introduced
  by 0.2.0's GUI work).
- Wired up 17 round-trip fidelity tests that had never run in CI
  despite their fixture data being committed (hardcoded
  `/tmp/rc505-dump` path with no way to point it at the checked-in
  `rc0-files.tar.gz`).
- Single-sourced the package version from `eastlight.__version__`
  (was duplicated in `pyproject.toml` and had already drifted from a
  hardcoded test assertion).
- Various packaging/CI fixes: `setuptools>=77`/`PyQt6>=6.7` floors,
  `MANIFEST.in` for a complete sdist, `publish.yml` now runs tests and
  checks the release tag matches the package version before
  publishing, GUI tests now actually run in CI (PyQt6 +
  `QT_QPA_PLATFORM=offscreen`).

### Known issues (updated from 0.2.0)

Still outstanding, deferred to a dedicated GUI fix pass:

- Input FX / Track FX / EQ / ASSIGN tabs are not implemented in the
  GUI (they're silently absent rather than crashing, as of the fix
  above — but still unusable for effects/EQ editing from the GUI).
- The GUI's own WAV import path still doesn't set track metadata or
  validate sample rate; use the CLI's `wav-import` (or `eastlight
  gui`'s import dialog once it's wired to `core.operations`).
- Several other GUI defects from the post-0.2.0 review (dead
  Copy/Swap context menu entries, full memory-list refresh cost on a
  real device, read-only-field display quirks) are not yet addressed.

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
