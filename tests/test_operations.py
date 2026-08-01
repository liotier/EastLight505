"""Tests for core.operations — shared logic between CLI and (future) GUI.

import_track_audio() is the single source of truth for importing audio
into a memory track: sample-rate validation, writing the WAV file, and
updating the track's RC0 metadata (has_audio, total_samples,
samples_per_measure, loop_length). Both the CLI's wav-import command and
the GUI should call this rather than reimplementing it — the GUI's own
copy previously diverged and silently omitted the metadata update.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from eastlight.core.library import RC505Library
from eastlight.core.operations import ImportResult, import_track_audio
from eastlight.core.parser import parse_memory_file
from eastlight.core.schema import SchemaRegistry
from eastlight.core.wav import DEVICE_SAMPLE_RATE, DEVICE_SUBTYPE


@pytest.fixture
def registry() -> SchemaRegistry:
    schema_dir = Path(__file__).parent.parent / "src" / "eastlight" / "schema"
    reg = SchemaRegistry()
    reg.load_all(schema_dir)
    return reg


@pytest.fixture
def roland_dir(tmp_path: Path, sample_rc0_content: str) -> Path:
    """ROLAND/ directory with memory 1 (tempo 70.0 BPM, per the fixture)."""
    root = tmp_path / "ROLAND"
    data = root / "DATA"
    wave = root / "WAVE"
    data.mkdir(parents=True)
    wave.mkdir(parents=True)
    (data / "MEMORY001A.RC0").write_text(sample_rc0_content, encoding="utf-8")
    return root


def _make_source_wav(path: Path, frames: int, sample_rate: int = DEVICE_SAMPLE_RATE) -> None:
    data = np.random.default_rng(42).uniform(-0.5, 0.5, (frames, 2)).astype(np.float32)
    sf.write(str(path), data, sample_rate, subtype=DEVICE_SUBTYPE)


class TestImportTrackAudio:
    def test_writes_wav_and_returns_result(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "source.wav"
        _make_source_wav(src, frames=22050)  # 0.5s

        lib = RC505Library(roland_dir, backup=False)
        result = import_track_audio(lib, registry, 1, 2, src)

        assert isinstance(result, ImportResult)
        assert result.frames == 22050
        assert result.duration == pytest.approx(0.5, abs=1e-6)

        dst = roland_dir / "WAVE" / "001_2" / "001_2.WAV"
        assert dst.exists()
        info = sf.info(str(dst))
        assert info.samplerate == DEVICE_SAMPLE_RATE
        assert info.channels == 2

    def test_sets_track_metadata(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        """Track1's tempo (700 = 70.0 BPM) implies samples_per_measure =
        44100*60/70*4 = 151200. Importing exactly 2 measures of audio
        should compute loop_length (S) = 2."""
        src = tmp_path / "source.wav"
        frames = 151200 * 2
        _make_source_wav(src, frames=frames)

        lib = RC505Library(roland_dir, backup=False)
        import_track_audio(lib, registry, 1, 1, src)

        rc0 = parse_memory_file(roland_dir / "DATA" / "MEMORY001A.RC0")
        track1 = rc0.mem["TRACK1"]
        assert track1["W"] == 1  # has_audio
        assert track1["X"] == frames  # total_samples
        assert track1["V"] == 151200  # samples_per_measure
        assert track1["S"] == 2  # loop_length in measures

    def test_result_reports_measures(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "source.wav"
        _make_source_wav(src, frames=151200 * 3)

        lib = RC505Library(roland_dir, backup=False)
        result = import_track_audio(lib, registry, 1, 1, src)
        assert result.measures == 3

    def test_saves_memory_with_backup(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "source.wav"
        _make_source_wav(src, frames=1000)

        backup_dir = tmp_path / "backups"
        lib = RC505Library(roland_dir, backup=True, backup_dir=backup_dir)
        import_track_audio(lib, registry, 1, 2, src)

        assert backup_dir.exists()  # save_memory triggered a backup

    def test_rejects_wrong_sample_rate(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "48k.wav"
        _make_source_wav(src, frames=1000, sample_rate=48000)

        lib = RC505Library(roland_dir, backup=False)
        with pytest.raises(ValueError, match="Sample rate mismatch"):
            import_track_audio(lib, registry, 1, 1, src)

        # No WAV should have been written for a rejected import
        assert not (roland_dir / "WAVE" / "001_1" / "001_1.WAV").exists()

    def test_rejects_invalid_track_number(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "source.wav"
        _make_source_wav(src, frames=1000)

        lib = RC505Library(roland_dir, backup=False)
        with pytest.raises(ValueError, match="Track number must be 1-5"):
            import_track_audio(lib, registry, 1, 6, src)
        with pytest.raises(ValueError, match="Track number must be 1-5"):
            import_track_audio(lib, registry, 1, 0, src)

    def test_rejects_nonexistent_memory(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "source.wav"
        _make_source_wav(src, frames=1000)

        lib = RC505Library(roland_dir, backup=False)
        with pytest.raises(ValueError, match="does not exist"):
            import_track_audio(lib, registry, 99, 1, src)

    def test_mono_source_converted_to_stereo(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        src = tmp_path / "mono.wav"
        data = np.zeros(11025, dtype=np.float32)
        sf.write(str(src), data, DEVICE_SAMPLE_RATE, subtype="PCM_16")

        lib = RC505Library(roland_dir, backup=False)
        import_track_audio(lib, registry, 1, 2, src)

        dst = roland_dir / "WAVE" / "001_2" / "001_2.WAV"
        info = sf.info(str(dst))
        assert info.channels == 2

    def test_overwrites_existing_track_audio(
        self, roland_dir: Path, registry: SchemaRegistry, tmp_path: Path
    ) -> None:
        """import_track_audio itself does not prompt for confirmation —
        that's a caller (CLI/GUI) concern. It always overwrites."""
        wav_dir = roland_dir / "WAVE" / "001_1"
        wav_dir.mkdir(parents=True)
        _make_source_wav(wav_dir / "001_1.WAV", frames=500)

        src = tmp_path / "new.wav"
        _make_source_wav(src, frames=2000)

        lib = RC505Library(roland_dir, backup=False)
        result = import_track_audio(lib, registry, 1, 1, src)
        assert result.frames == 2000

        info = sf.info(str(wav_dir / "001_1.WAV"))
        assert info.frames == 2000
