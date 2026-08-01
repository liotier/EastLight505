# Hardware verification checklist

Questions that can only be answered by testing against a real RC-505 mk2.
Report findings back and we'll update the schema/docs accordingly.

For software validation (does the fixed code actually work against real
hardware, not just static dump files), see
**[TESTING_PROTOCOL.md](TESTING_PROTOCOL.md)** — this file only covers
the remaining schema-mapping questions.

## 1. Tempo source

Same real memory (`MEMORY001A.RC0`) reports two different tempos depending
on which field you read:

- `MASTER.tempo_x10` (tag A) = 1228 → 122.8 BPM
- `TRACK1.U` (tag U) = 1200 → 120.0 BPM

**Question:** Which one does the device display as *the* memory's tempo
(e.g. on the main screen, or in a patch list)? The CLI's `list` command
currently reads `TRACK.U` of the first track with audio; the GUI's memory
list reads `MASTER.tempo_x10`. They disagree and only one can be right.

## 2. CTL FUNC values above 200

Your transcription (thank you!) covered 0–200 and we assumed that was the
full range. But real device data contains values past it:

- `ICTL3_PEDAL4.A` = 202
- `ICTL3_PEDAL5.A` = 203
- `ICTL3_PEDAL6.A` = 204
- `ECTL_CTL1.A` = 210
- `ECTL_CTL2.A` = 211
- `ECTL_CTL4.A` = 207

**Question:** What are the CTL FUNC names for 201 and up? What's the true
maximum? (Same method as before: MENU → CTRL, scroll past 200.)

## 3. CTL FUNC preferences

Found under **MENU → CTL FUNC → PREF** on the device:

- MODE PLAY (SYSTEM/MEMORY)
- MODE UNDO (SYSTEM/MEMORY)
- QUICK CLEAR (ON/OFF)
- ALL CLEAR (ON/OFF)

**Question:** Which RC0 section/field stores each of these? Method:
note current value, USB-backup, flip one setting, USB-backup again, diff
the two `SYSTEM1.RC0` files. Repeat per setting (or do all four in one
pass if you're systematic about which changed).

## 4. INPUT preferences

Found under **MENU → INPUT → SETUP → page 3**:

- MIC (SYSTEM/MEMORY)
- INST1 (SYSTEM/MEMORY)
- INST2 (SYSTEM/MEMORY)

**Question:** Same as above — which field stores each? Same diff method.

## 5. SETUP fields R–V

We've mapped SETUP A–Q (current memory, display mode, contrast, auto-off,
indicator, knob functions ×4, memory extents, loop status colors ×5).
Fields R–V (5 fields) have no known menu item and are currently marked
`reserved` / `read_only` in the schema.

**Question:** Does the SETUP menu have anything beyond what's listed above?
If you've been through the whole menu and found nothing else, that
confirms R–V are internal/firmware-only — worth an explicit "confirmed
reserved" note either way.

## 6. ASSIGN field ranges

Our schema's declared ranges are too narrow for real stored data:

- `ASSIGN2.H` (target_max) = 903, schema says `[0, 255]`
- `ASSIGN3.F` (act_hi) = 255, schema says `[0, 127]`
- 12 fields total exceed their declared range across the real dump

**Question:** What are the actual valid ranges for ASSIGN target/act
fields? This affects the CLI's `--dry-run` range-validation warnings,
which currently fire false positives on legitimate stored values.

## 7. TRACK6 confirmation

You've already confirmed TRACK6 is not user-accessible on the RC-505 mk2
(likely an artifact of the shared RC-505mk2/RC-600 codebase — RC-600 may
use it). No action needed unless you spot something that contradicts
this, e.g. TRACK6 appearing anywhere in a menu or having audio after
some device operation we haven't tried.
