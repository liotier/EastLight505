# EastLight

Open-source editor/librarian for the **Roland RC-505 MK2** loop station — CLI and GUI.

EastLight reads and writes the RC-505 MK2's SD card backup format (`ROLAND/` directory), giving you full control over memory patches, audio tracks, effects, and system settings from the terminal or from a graphical interface.

> **v0.2.0 — Alpha release.** The file format parser achieves byte-for-byte round-trip fidelity and ~98% schema coverage. Back up your SD card before using EastLight on real data.

## Install

### With pipx (recommended)

```
pipx install "eastlight[gui]"
```

Leave off `[gui]` for CLI-only. See [Install docs](https://liotier.github.io/EastLightRC-505mk2Librarian/install/) for pip and from-source options, plus pipx troubleshooting if you installed without `[gui]` and need to add it later.

### From source

```
git clone https://github.com/liotier/EastLightRC-505mk2Librarian.git
cd EastLightRC-505mk2Librarian
pip install -e ".[gui]"
```

### Requirements

- **Python 3.11+**
- **libsndfile** — required by the `soundfile` dependency for audio I/O

libsndfile is bundled automatically on Windows and macOS. On Linux, install it with your package manager:

```
# Debian / Ubuntu
sudo apt install libsndfile1

# Fedora
sudo dnf install libsndfile

# Arch
sudo pacman -S libsndfile
```

### Verify installation

```
eastlight --version
eastlight --help
```

## Graphical interface

Launch the GUI with:

```
eastlight gui
```

Or point it at a specific ROLAND/ directory:

```
eastlight gui -d /media/user/RC505/ROLAND
```

The GUI provides:

- **Memory list** — browse all 99 slots with name, track count, and tempo
- **Parameter editor** — tabbed, schema-driven editors for every section (tracks, master, FX, mixer, routing, EQ, etc.)
- **System settings** — edit SETUP, PREF, MIDI, USB, INPUT, and COLOR settings
- **WAV import/export** — import audio files, export tracks
- **Undo/redo** — full undo stack for parameter edits
- **Device detection** — auto-detect connected RC-505 MK2 devices

Requires `pipx install "eastlight[gui]"` (adds PyQt6).

## Getting started (CLI)

### 1. Connect your RC-505 MK2

Connect via USB and mount the SD card (the device appears as a USB mass storage device), then point EastLight at the `ROLAND/` directory:

```
eastlight detect
eastlight config --set-dir /media/user/RC505/ROLAND
```

Once a default directory is set, all commands use it automatically. Override anytime with `-d /path/to/ROLAND`.

### 2. Browse and inspect memories

```
eastlight list                        # All 99 memory slots
eastlight show 1                      # Full details for memory 1
eastlight show 1 -s TRACK1            # Just track 1 parameters
eastlight show 1 --raw                # Raw field values
```

### 3. Edit parameters

```
eastlight set 1 MASTER pan 75
eastlight name 1 "My Loop"
eastlight set 1 TRACK1 play_level 100 --dry-run   # Preview without writing
```

All write commands support `--dry-run` / `-n` to preview changes safely.

## Command reference

### Memory management

| Command | Description |
|---------|-------------|
| `eastlight list` | List all 99 memory slots with names, tracks, tempo |
| `eastlight show <mem>` | Show parameters for a memory (`-s SECTION` to filter) |
| `eastlight set <mem> <section> <param> <value>` | Set a parameter value |
| `eastlight name <mem> <name>` | Rename a memory slot (max 12 characters) |
| `eastlight copy <src> <dst>` | Copy a memory slot (RC0 + WAV audio) |
| `eastlight swap <a> <b>` | Swap two memory slots |
| `eastlight clear <mem>` | Clear a memory slot (with automatic backup) |
| `eastlight diff <a> <b>` | Show differences between two memories |

### Batch operations

| Command | Description |
|---------|-------------|
| `eastlight bulk-set <range> <section> <param> <value>` | Set a parameter across multiple memories |
| `eastlight template-export <mem> <file>` | Export a memory's parameters as YAML |
| `eastlight template-apply <file> <range>` | Apply a YAML template to one or more memories |

Memory ranges support commas and dashes: `1-5`, `1,3,5`, `1-3,7,10-12`.

```
eastlight bulk-set 1-10 MASTER play_level 100
eastlight template-export 1 my_settings.yaml
eastlight template-export 1 fx_only.yaml -s TRACK1 -s MASTER
eastlight template-apply my_settings.yaml 5
eastlight template-apply settings.yaml 1-10 --dry-run
```

### Audio import/export

| Command | Description |
|---------|-------------|
| `eastlight wav-info <mem>` | Show WAV audio info for all tracks |
| `eastlight wav-export <mem> <track> <file>` | Export a track's audio |
| `eastlight wav-import <mem> <track> <file>` | Import an audio file into a track |

```
eastlight wav-export 1 1 my_loop.wav
eastlight wav-export 1 1 my_loop.wav --format pcm24
eastlight wav-import 1 2 recording.wav
```

Supported import formats: WAV, FLAC, OGG (anything libsndfile supports). Audio is automatically converted to 32-bit float stereo at 44.1 kHz (the device's native format). Mono files are duplicated to stereo.

### Effects

| Command | Description |
|---------|-------------|
| `eastlight fx-show <mem> <ifx\|tfx>` | Show FX chain parameters |
| `eastlight fx-set <mem> <ifx\|tfx> <slot> <param> <value>` | Set an FX parameter |

```
eastlight fx-show 1 ifx                       # All input FX
eastlight fx-show 1 tfx -g A                  # Track FX group A
eastlight fx-show 1 ifx -s AA                 # Specific slot
eastlight fx-set 1 ifx AA feedback 30
eastlight fx-set 1 ifx AA fx_type 35 --dry-run
```

70 effect types fully mapped: filters, modulation, delay, reverb, dynamics, pitch, vocoder, slicer, and 4 TFX-exclusive beat effects.

### System settings

| Command | Description |
|---------|-------------|
| `eastlight sys-show` | Show system settings (`-s SECTION` to filter, `--all` for everything) |
| `eastlight sys-set <section> <param> <value>` | Set a system parameter |

```
eastlight sys-show -s SETUP
eastlight sys-set SETUP contrast 8
eastlight sys-set PREF pref_eq 0 --dry-run
```

### MIDI controller assignments

| Command | Description |
|---------|-------------|
| `eastlight ctl-show` | Show controller assignments (`--type ictl` or `--type ectl`) |
| `eastlight ctl-set <instance> <param> <value>` | Set a controller assignment |

```
eastlight ctl-show --type ectl
eastlight ctl-set ICTL1_TRACK1_FX ctl_func 42
eastlight ctl-set ECTL_CTL1 ctl_func 10
eastlight ctl-set ECTL_EXP1 ctl_range 64
```

Internal controllers (ICTL): 47 panel button and pedal assignments across 3 banks.
External controllers (ECTL): 6 MIDI CC inputs (CTL1-4, EXP1-2).
All 201 CTL FUNC values are mapped to human-readable names with push/hold/click sub-actions.

### Backup management

| Command | Description |
|---------|-------------|
| `eastlight backup list` | List all automatic backups |
| `eastlight backup show <timestamp>` | Show backup details |
| `eastlight backup restore <timestamp>` | Restore a backup |
| `eastlight backup prune --keep <n>` | Remove old backups |

EastLight automatically backs up files before any write operation. Backups are timestamped and stored in `~/.config/eastlight/backups/` (outside the device filesystem).

### Configuration

| Command | Description |
|---------|-------------|
| `eastlight config --show` | Show current configuration |
| `eastlight config --set-dir <path>` | Set default ROLAND/ directory |
| `eastlight config --no-backup` | Disable automatic backups |
| `eastlight detect` | Auto-detect connected RC-505 MK2 devices |

Configuration is stored in `~/.config/eastlight/config.yaml`.

**ROLAND/ directory resolution order:**

1. Explicit `-d/--dir` option
2. Default from `eastlight config --set-dir`
3. Single auto-detected device (USB mount scan)

### Utility

| Command | Description |
|---------|-------------|
| `eastlight parse <file>` | Parse and display raw structure of an RC0 file |
| `eastlight --version` | Show version |
| `eastlight --help` | Show help |

## Safety

All write commands create an automatic backup before modifying any files. Use `--dry-run` to preview changes first.

```
eastlight set 1 MASTER pan 75 --dry-run
eastlight clear 5 -n
eastlight bulk-set 1-10 MASTER play_level 100 -n
```

To disable automatic backups: `eastlight config --no-backup`

## Schema coverage

~98% of the RC-505 MK2's file format is mapped:

- All memory-level sections (track, master, EQ, mixer, routing, assign, ...)
- All 70 FX effect types (66 shared + 4 TFX-exclusive)
- FX type index enum with reverse lookup
- System settings (SETUP, PREF, COLOR, USB, MIDI)
- All 47 ICTL + 6 ECTL controller mapping sections
- All 201 CTL FUNC values (0-200) with push/hold/click sub-actions

Remaining gaps: 5 SETUP fields (R-V, likely reserved/internal — no known menu item), 4 CTL FUNC preferences (MODE PLAY, MODE UNDO, QUICK CLEAR, ALL CLEAR), 3 INPUT preferences (MIC/INST1/INST2 SYSTEM/MEMORY toggle). See [dev/HARDWARE_TESTS.md](dev/HARDWARE_TESTS.md) for the outstanding verification list and the [feasibility study](dev/rc505-mk2-feasibility.md) for background.

## Development

```
git clone https://github.com/liotier/EastLightRC-505mk2Librarian.git
cd EastLightRC-505mk2Librarian
pip install -e ".[dev]"
pytest
```

## License

GPL-3.0-or-later
