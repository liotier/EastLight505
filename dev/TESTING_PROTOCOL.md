# Hardware testing protocol

Everything here has been verified against static device-dump files
(committed as `rc0-files.tar.gz`) and, where possible, against your real
`MEMORY001A.RC0`. What's never been tested is round-tripping through the
**actual device** — writing a file back to the SD card and confirming
the RC-505 mk2 itself reads it correctly. That's what this protocol is
for.

Ordered from safest to riskiest. Stop and report back if anything in an
earlier tier fails — no point testing writes if reads are broken.

## 0. Setup

Install the branch under test (not yet released/merged):

```bash
git clone https://github.com/liotier/EastLightRC-505mk2Librarian.git
cd EastLightRC-505mk2Librarian
git checkout claude/rc505-mk2-feasibility-Sbx2K
pip install -e ".[gui]"
```

Connect the RC-505 mk2 via USB, mount the SD card, then:

```bash
eastlight detect
eastlight config --set-dir /path/to/ROLAND
```

**Before anything else: make your own manual backup of the SD card's
`ROLAND/` directory**, copied somewhere outside EastLight's control.
EastLight's automatic backups (`~/.config/eastlight/backups/`) are a
safety net, not a replacement for this — verify the manual copy exists
before proceeding.

## 1. Read-only smoke test (zero risk)

Nothing here writes to the SD card. Just confirm no crashes and the
output looks sane.

```bash
eastlight list
eastlight show 1
eastlight sys-show --all
eastlight ctl-show
eastlight fx-show 1 ifx
eastlight fx-show 1 tfx
eastlight wav-info 1
eastlight diff 1 2
```

**Specifically check `diff`'s output** — this is the command most
directly affected by the collision bug we fixed. Pick two memories you
know have *different* input-FX settings but similar/identical track FX,
and confirm `diff` reports the IFX difference (look for an `IFX.<name>`
table in the output). Before the fix, this would have been silently
missed.

## 2. Backup and restore (low risk — test on a scratch write)

Verify the safety net actually works before relying on it for anything
else in this protocol.

```bash
eastlight set 1 MASTER pan 75 --dry-run    # confirm dry-run touches nothing
eastlight backup list                       # should be empty/minimal so far

eastlight set 1 MASTER pan 75               # real write, auto-backs-up first
eastlight backup list                       # should now show one snapshot

eastlight backup restore <timestamp-from-above>
eastlight show 1 -s MASTER                  # confirm pan is back to its original value
```

## 3. Round-trip write-back verification (medium risk)

This is the one thing that's never been tested against real hardware:
does the device still read a file after EastLight writes it back
*unchanged*?

```bash
# Pick a memory slot you don't mind touching (or use one after copying
# it to a scratch slot — step 4 below).
eastlight show 5 > /tmp/before.txt
eastlight set 5 MASTER pan 75          # any trivial, reversible change
eastlight set 5 MASTER pan <original-value>   # set it back
eastlight show 5 > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt    # should be empty
```

Then, critically: **eject the SD card, put it back in the device, power
it on, and confirm memory 5 loads and plays correctly** — same tempo,
same effects, same name, no error screen. This is the real test; the
`diff` above only proves EastLight is internally consistent, not that
the device agrees.

## 4. Organize operations (medium risk — use scratch slots)

Pick a slot you don't care about (e.g. an empty one, or copy something
disposable into it first) and exercise:

```bash
eastlight copy 1 90              # copy into a scratch slot
eastlight name 90 "Test Copy"
eastlight swap 90 91
eastlight clear 91 --dry-run     # preview first
eastlight clear 91               # confirm it actually clears
```

After each, power-cycle the device (or at minimum navigate to the
affected slots on the device UI) and confirm it reflects what you'd
expect — no corruption, no "invalid memory" errors.

## 5. FX editing and the template fix (medium risk)

This directly exercises the bug we fixed — templates and bulk edits
previously silently dropped or corrupted input-FX data.

```bash
# Export a memory with distinct IFX and TFX settings
eastlight template-export 1 /tmp/test_template.yaml

# Inspect the file — confirm BOTH _ifx_sections and _tfx_sections are
# present and non-empty, with the values matching `eastlight fx-show 1 ifx`
# and `eastlight fx-show 1 tfx` respectively.
cat /tmp/test_template.yaml | head -50

# Apply it to a scratch slot
eastlight template-apply /tmp/test_template.yaml 90 --dry-run
eastlight template-apply /tmp/test_template.yaml 90

# Confirm slot 90's IFX settings now match memory 1's (not memory 90's
# old TFX settings duplicated into IFX — the old bug)
eastlight diff 1 90
```

Then on the device: load memory 90, confirm the input effect is what
you expect (not silently absent, not the track effect's settings).

Also test a direct FX edit:

```bash
eastlight fx-set 1 ifx AA feedback 30 --dry-run
eastlight fx-set 1 ifx AA feedback 30
```

Confirm on the device that Input FX slot A:A actually reflects the new
feedback value.

## 6. WAV import metadata fix (medium risk)

This verifies the extracted `import_track_audio` still does the right
thing when it matters — the device actually recognizing the imported
audio, not just EastLight's own view of the metadata.

```bash
eastlight wav-import 90 3 /path/to/some/test.wav --force
eastlight wav-info 90 -t 3
```

Then on the device: load memory 90, confirm track 3 shows the imported
audio (correct length, plays back correctly, tempo sync looks right if
the track had a tempo set).

## 7. GUI smoke test (low risk, read-mostly)

The GUI's known limitations (from the CHANGELOG's Known Issues): FX/EQ/
ASSIGN tabs are not implemented (silently absent, not crashing), and its
own WAV import doesn't set metadata — use the CLI for that (step 6).

```bash
eastlight gui
```

- Browse several memories, including ones with heavy FX use — confirm
  no crash (this used to crash on every memory with any FX; verified
  fixed against your dump files, but worth confirming live).
- Confirm the Tracks and Master tabs show correct values.
- Try Undo after a parameter edit — confirm the displayed value updates
  (previously it wouldn't, even though the underlying data had reverted).
- Don't rely on it for FX/EQ/ASSIGN editing yet.

## 8. Hardware data collection

Separate from software validation — these are questions about the
device's actual behavior/menus, needed to close the last schema gaps.
See **[HARDWARE_TESTS.md](HARDWARE_TESTS.md)** for the full list:
tempo source, CTL FUNC values above 200, CTL FUNC preferences, INPUT
preferences, SETUP R–V confirmation, ASSIGN range maxima.

---

Report back whatever you find, including anything that looks *fine* —
knowing tier 3 passed cleanly is as useful as knowing it didn't.
