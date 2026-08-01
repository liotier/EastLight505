# Sample device dumps

`MEMORY001A.RC0` — a single standalone memory file, committed early in
the project (before `rc0-files.tar.gz` existed) as a reference sample
for the initial format reverse-engineering work.

**Not used by any code, test, or CI step** — the test suite's real
fixture data is `rc0-files.tar.gz` at the repo root, extracted via
`EASTLIGHT_DUMP_DIR` (see `tests/conftest.py`'s `dump_dir` fixture).

Note: this file's content **differs** from `ROLAND/DATA/MEMORY001A.RC0`
inside `rc0-files.tar.gz` — they're snapshots of the same device slot
taken at different times (tempo, track state, and sample counts all
differ). Kept here for historical/reference purposes only; don't treat
it as authoritative for anything the tarball also covers.
