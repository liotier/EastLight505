# Command reference

All write commands support `--dry-run` / `-n` to preview changes without writing. EastLight automatically creates backups before every write operation.

## Memory management

### `eastlight list`

List all 99 memory slots with names, track indicators, tempo, and backup status.

```bash
eastlight list
eastlight list -d /media/user/RC505/ROLAND
```

### `eastlight show <memory>`

Show parameters for a memory slot.

```bash
eastlight show 1                  # All sections
eastlight show 1 -s TRACK1        # Specific section
eastlight show 1 --raw            # Raw numeric values
```

### `eastlight set <memory> <section> <param> <value>`

Set a parameter value. Validates against schema-defined ranges.

```bash
eastlight set 1 MASTER pan 75
eastlight set 1 TRACK1 play_level 100 --dry-run
```

### `eastlight name <memory> <name>`

Rename a memory slot (max 12 characters).

```bash
eastlight name 1 "My Loop"
```

### `eastlight copy <source> <destination>`

Copy a memory slot including RC0 data and WAV audio files.

```bash
eastlight copy 1 50
```

### `eastlight swap <a> <b>`

Swap two memory slots.

```bash
eastlight swap 1 50
```

### `eastlight clear <memory>`

Clear a memory slot — removes RC0 data and WAV audio. Creates a backup first.

```bash
eastlight clear 5
eastlight clear 5 --dry-run
```

### `eastlight diff <a> <b>`

Show parameter differences between two memories.

```bash
eastlight diff 1 50
```

## Batch operations

### `eastlight bulk-set <range> <section> <param> <value>`

Apply the same parameter change across multiple memories.

```bash
eastlight bulk-set 1-10 MASTER play_level 100
eastlight bulk-set 1,3,5 TRACK1 pan 50 --dry-run
```

Memory ranges support commas and dashes: `1-5`, `1,3,5`, `1-3,7,10-12`.

### `eastlight template-export <memory> <file>`

Export a memory's parameters as a YAML file (no audio).

```bash
eastlight template-export 1 my_settings.yaml
eastlight template-export 1 fx_only.yaml -s TRACK1 -s MASTER
```

### `eastlight template-apply <file> <range>`

Apply a YAML template to one or more memories.

```bash
eastlight template-apply my_settings.yaml 5
eastlight template-apply settings.yaml 1-10 --dry-run
```

## Audio

### `eastlight wav-info <memory>`

Show WAV audio information for all tracks in a memory.

```bash
eastlight wav-info 1
```

### `eastlight wav-export <memory> <track> <file>`

Export a track's audio to a file. Default format is 32-bit float WAV (lossless).

```bash
eastlight wav-export 1 1 my_loop.wav
eastlight wav-export 1 1 my_loop.wav --format pcm24
```

### `eastlight wav-import <memory> <track> <file>`

Import an audio file into a memory track. Supports WAV, FLAC, OGG (anything libsndfile handles). Audio is converted to 32-bit float stereo at 44.1 kHz. Mono files are duplicated to stereo.

```bash
eastlight wav-import 1 2 recording.wav
```

## Effects

### `eastlight fx-show <memory> <ifx|tfx>`

Show FX chain parameters.

```bash
eastlight fx-show 1 ifx                 # All input FX
eastlight fx-show 1 tfx -g A            # Track FX group A
eastlight fx-show 1 ifx -s AA           # Specific slot
```

### `eastlight fx-set <memory> <ifx|tfx> <slot> <param> <value>`

Set an FX parameter value.

```bash
eastlight fx-set 1 ifx AA feedback 30
eastlight fx-set 1 ifx AA sw 1
eastlight fx-set 1 ifx AA fx_type 35 --dry-run
```

70 effect types are fully mapped: filters, modulation, delay, reverb, dynamics, pitch, vocoder, slicer, and 4 TFX-exclusive beat effects.

## System settings

### `eastlight sys-show`

Show system settings.

```bash
eastlight sys-show                       # Summary
eastlight sys-show -s SETUP              # Specific section
eastlight sys-show --all                 # Everything
```

### `eastlight sys-set <section> <param> <value>`

Set a system parameter.

```bash
eastlight sys-set SETUP contrast 8
eastlight sys-set PREF pref_eq 0 --dry-run
```

## MIDI controller assignments

### `eastlight ctl-show`

Show controller assignments.

```bash
eastlight ctl-show                       # All
eastlight ctl-show --type ictl           # Internal controllers only
eastlight ctl-show --type ectl           # External controllers only
```

### `eastlight ctl-set <instance> <param> <value>`

Set a controller assignment.

```bash
eastlight ctl-set ICTL1_TRACK1_FX ctl_func 42
eastlight ctl-set ECTL_CTL1 ctl_func 10
eastlight ctl-set ECTL_EXP1 ctl_range 64
eastlight ctl-set ICTL1_PEDAL1 ctl_mode 0
```

Internal controllers (ICTL): 47 panel button and pedal assignments across 3 banks.
External controllers (ECTL): 6 MIDI CC inputs (CTL1-4, EXP1-2).
All 201 CTL FUNC values (0-200) are mapped to human-readable names with push/hold/click sub-actions.

## Backup management

### `eastlight backup list`

List all automatic backups.

### `eastlight backup show <timestamp>`

Show details of a specific backup.

### `eastlight backup restore <timestamp>`

Restore files from a backup.

### `eastlight backup prune --keep <n>`

Remove old backups, keeping the most recent `n`.

```bash
eastlight backup prune --keep 3
```

Backups are timestamped and stored in `~/.config/eastlight/backups/` (outside the device filesystem).

## Configuration

### `eastlight config`

View or modify configuration.

```bash
eastlight config --show
eastlight config --set-dir /media/user/RC505/ROLAND
eastlight config --no-backup
```

Configuration is stored in `~/.config/eastlight/config.yaml`.

### `eastlight detect`

Auto-detect connected RC-505 MK2 devices by scanning USB mount points.

### `eastlight parse <file>`

Parse and display raw structure of an RC0 file. Useful for debugging.

```bash
eastlight parse /media/user/RC505/ROLAND/DATA/MEMORY001A.RC0
```
