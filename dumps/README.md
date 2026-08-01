# Dump collection for schema gap filling

## 1. CTL FUNC map — DONE

All 201 CTL FUNC values (0-200) mapped with push/hold/click sub-actions.
Integrated into `src/eastlight/schema/ctl_func.yaml` and displayed by
`ctl-show` and `ctl-set`.

## 2. SETUP fields — DONE (mostly)

Fields A-Q are all mapped, including the knob functions and loop status
colors that were originally unknown:

| Tag | Name |
|-----|------|
| A | Current Memory |
| B | Display Mode (COLOR/MONO/SIMPLIFIED) |
| C | Memory Extent Max |
| D | Contrast |
| E | Auto Off |
| F | Indicator (TYPE1/TYPE2/OFF) |
| G | FX Knob Mode (DIRECT/TOGGLE) |
| H | Knob Func 1 |
| I | Memory Extent Min |
| J-L | Knob Func 2-4 |
| M-Q | Loop Status colors (REC/PLAY/DUB/STOP/BLANK) |

Fields R-V (5 fields) have no known menu item and are marked
`reserved`/`read_only` in the schema. See `HARDWARE_TESTS.md` item 5 for
the outstanding confirmation.

## 3. PREF fields — DONE

All 20 fields (A-T) are mapped. The final 6 (O-T) turned out to be
CTL1-4 and EXP1-2 SYSTEM/MEMORY toggles, found under
MENU → CTL FUNC → PREF on the device — a different menu than expected
when this file was first written.

## Remaining gaps

See `../HARDWARE_TESTS.md` for the full list of outstanding
hardware-verification questions:

- CTL FUNC values above 200 (real device data goes at least to 211)
- CTL FUNC preferences: MODE PLAY, MODE UNDO, QUICK CLEAR, ALL CLEAR
- INPUT preferences: MIC, INST1, INST2 (SYSTEM/MEMORY toggles)
- SETUP R-V: confirm genuinely reserved (no menu item found so far)
- ASSIGN field range maxima (real data exceeds declared schema ranges)
