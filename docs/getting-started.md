# Getting started

## 1. Connect your RC-505 MK2

Connect the RC-505 MK2 via USB. It appears as a USB mass storage device with a `ROLAND/` directory on the SD card.

Auto-detect connected devices:

```bash
eastlight detect
```

Set the default directory so you don't have to specify it every time:

```bash
eastlight config --set-dir /media/user/RC505/ROLAND
```

All commands will now use this directory automatically. You can always override with `-d /path/to/ROLAND`.

## 2. Browse memories

List all 99 memory slots:

```bash
eastlight list
```

This shows memory names, which tracks have audio, tempo, and backup status.

## 3. Inspect a memory

```bash
eastlight show 1                  # Full details
eastlight show 1 -s TRACK1        # Just track 1
eastlight show 1 -s MASTER        # Just master section
eastlight show 1 --raw            # Raw field values
```

## 4. Make changes

Always preview with `--dry-run` first:

```bash
eastlight set 1 MASTER pan 75 --dry-run
```

Then apply:

```bash
eastlight set 1 MASTER pan 75
eastlight name 1 "My Loop"
```

EastLight automatically creates a timestamped backup before writing.

## 5. Organize your memories

```bash
eastlight copy 1 50               # Copy memory 1 to slot 50
eastlight swap 1 50               # Swap two slots
eastlight clear 5                 # Clear a slot
eastlight diff 1 50               # Compare two memories
```

## ROLAND/ directory resolution

Commands find the `ROLAND/` directory in this order:

1. Explicit `-d/--dir` option
2. Default from `eastlight config --set-dir`
3. Single auto-detected device (USB mount scan)

If multiple devices are detected and no default is set, EastLight lists them and asks you to choose.
