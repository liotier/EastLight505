# Schema coverage

EastLight uses a schema-driven architecture: YAML files define the mapping between the RC-505 MK2's positional single-letter XML tags and human-readable parameter names.

## Coverage summary

~98% of the RC-505 MK2's file format is mapped:

| Area | Status |
|------|--------|
| Memory sections (TRACK, MASTER, EQ, MIXER, ROUTING, ASSIGN, ...) | Complete |
| FX effect types (70 types, all parameters) | Complete |
| FX type index enum (IFX 0-65, TFX 0-69) | Complete |
| System settings (SETUP, PREF, COLOR, USB, MIDI) | Complete |
| Internal controllers (ICTL) — 47 sections across 3 banks | Complete |
| External controllers (ECTL) — 6 sections | Complete |
| CTL FUNC enum — 201 values with sub-actions | Complete |
| NAME encoding (ASCII, 12 chars) | Complete |
| WAV format (32-bit float, stereo, 44.1 kHz) | Complete |

## Known gaps

These fields exist on the device but their RC0 storage location has not been identified:

- **SETUP fields J-V** (13 fields) — reserved/unknown purpose
- **PREF fields O-T** (6 fields) — reserved/unknown purpose
- **CTL FUNC preferences** — MODE PLAY (SYSTEM/MEMORY), MODE UNDO (SYSTEM/MEMORY), QUICK CLEAR (ON/OFF), ALL CLEAR (ON/OFF). Found under MENU -> CTL FUNC -> PREF on the device.
- **INPUT preferences** — MIC, INST1, INST2 (each SYSTEM/MEMORY). Found under MENU -> INPUT -> SETUP -> page 3. Controls whether input settings come from global system or per-memory.

These gaps do not affect data integrity — EastLight preserves all fields during round-trip read/write, including unmapped ones.

## Schema files

```
src/eastlight/schema/
  track.yaml          Track parameters (A-Y)
  master.yaml         Master output parameters
  eq.yaml             EQ parameters
  mixer.yaml          Mixer routing
  routing.yaml        Signal routing matrix
  assign.yaml         MIDI assign sections
  rec.yaml            Recording parameters
  play.yaml           Playback parameters
  rhythm.yaml         Rhythm settings
  name.yaml           Memory name (ASCII encoding)
  input.yaml          Input settings
  output.yaml         Output settings
  setup.yaml          System setup
  pref.yaml           System preferences
  color.yaml          Display colors
  usb.yaml            USB settings
  midi.yaml           MIDI settings
  ictl.yaml           Internal controller assignments
  ectl.yaml           External controller assignments
  fx_setup.yaml       FX chain configuration
  fx_slot.yaml        FX slot header
  fx_subslot.yaml     FX sub-slot parameters
  master_fx.yaml      Master FX
  fixed_value.yaml    Fixed value assignments
  ctl_func.yaml       CTL FUNC enum (201 entries)
  fx_types.yaml       FX type index enum
  effects/*.yaml      70 individual effect type schemas
```

## Contributing mappings

If you discover what an unmapped field does (via before/after USB backup comparison), contributions are welcome. Edit the relevant YAML file and submit a pull request.
