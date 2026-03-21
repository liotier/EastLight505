# Effects reference

The RC-505 MK2 has two FX chains:

- **IFX** (Input FX) — applied to incoming audio before recording. 4 groups (A-D) with 4 slots each (AA, AB, AC, AD, BA, ...).
- **TFX** (Track FX) — applied to recorded tracks during playback. Same 4x4 structure.

IFX supports 66 effect types (indices 0-65). TFX supports 70 effect types (indices 0-69), including 4 beat-synced effects exclusive to TFX.

## Viewing effects

```bash
eastlight fx-show 1 ifx                 # All input FX for memory 1
eastlight fx-show 1 tfx                 # All track FX
eastlight fx-show 1 tfx -g A            # Group A only
eastlight fx-show 1 ifx -s AA           # Specific slot with all parameters
```

## Editing effects

```bash
eastlight fx-set 1 ifx AA sw 1                    # Enable slot
eastlight fx-set 1 ifx AA fx_type 35               # Change effect type
eastlight fx-set 1 ifx AA feedback 30              # Set a parameter
eastlight fx-set 1 ifx AA fx_type 35 --dry-run     # Preview first
```

## Effect types

Each effect type has its own set of parameters. When you change `fx_type`, the slot's parameters change accordingly.

### Shared effects (IFX and TFX, indices 0-65)

Filters, EQ, dynamics, modulation, delay, reverb, pitch, vocoder, slicer, and more.

### TFX-exclusive effects (indices 66-69)

Four beat-synced effects available only on TFX:

- **Beat Scatter** (66)
- **Beat Repeat** (67)
- **Beat Shift** (68)
- **Beat Transform** (69)

## Tips

- Use `fx-show` with `-s` to see all available parameters for the current effect type in a slot
- Use `--dry-run` when changing `fx_type` to verify the new type index is valid
- Effect parameters are type-specific — changing `fx_type` resets them to defaults on the device
