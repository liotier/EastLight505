# EastLight

Open-source **command-line** editor/librarian for the **Roland RC-505 MK2** loop station.

EastLight reads and writes the RC-505 MK2's SD card backup format (`ROLAND/` directory), giving you full control over memory patches, audio tracks, effects, and system settings from the terminal.

!!! warning "Alpha release (v0.1.0)"
    The file format parser achieves byte-for-byte round-trip fidelity and ~98% schema coverage, but the CLI interface and edge cases are still maturing. **Back up your SD card before using EastLight on real data.**

## Features

- **Browse and edit** all 99 memory slots — parameters, names, effects, system settings
- **Copy, swap, clear** memories with automatic backup
- **Batch operations** — apply changes across multiple memories at once
- **Template system** — export/import memory settings as YAML
- **Audio import/export** — WAV, FLAC, OGG via libsndfile
- **70 effect types** fully mapped with all parameters
- **201 controller functions** mapped to human-readable names
- **Dry-run mode** on every write command — preview before committing
- **Automatic backups** before every write operation

## Quick example

```bash
# Point EastLight at your RC-505 MK2
eastlight detect
eastlight config --set-dir /media/user/RC505/ROLAND

# Browse memories
eastlight list
eastlight show 1

# Edit parameters
eastlight set 1 MASTER pan 75
eastlight name 1 "My Loop"

# Batch operations
eastlight bulk-set 1-10 MASTER play_level 100

# Export/import audio
eastlight wav-export 1 1 my_loop.wav
eastlight wav-import 1 2 recording.wav
```

## What's next

- Graphical interface (PyQt6) — planned for a future release
- Full schema coverage for remaining system fields
- Rhythm pattern editing

## License

GPL-3.0-or-later
