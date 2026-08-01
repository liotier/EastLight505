"""High-level operations composing library, model, and wav — the shared
logic behind CLI commands and (eventually) GUI actions.

The point of this module is to give both front-ends a single source of
truth for anything more involved than a plain field write, so behavior
can't silently diverge between them (as happened with the CLI's
wav-import metadata handling and the GUI's own, incomplete copy of it).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .library import RC505Library
from .model import Memory
from .schema import SchemaRegistry
from .wav import DEVICE_SAMPLE_RATE, import_audio, wav_write_device


@dataclass
class ImportResult:
    """Result of a successful import_track_audio() call."""

    frames: int
    duration: float
    measures: int | None  # None if the track has no tempo set


def import_track_audio(
    lib: RC505Library,
    registry: SchemaRegistry,
    memory_num: int,
    track_num: int,
    src: str | Path,
) -> ImportResult:
    """Import an audio file into a memory track and update RC0 metadata.

    Converts the source audio to the device's native format (32-bit
    float, stereo, 44.1kHz — see core.wav.import_audio), writes it to
    WAVE/, and updates the track's has_audio / total_samples /
    samples_per_measure / loop_length fields so the device actually
    recognizes the imported audio.

    Always overwrites any existing audio on the target track — callers
    that want a confirmation prompt should check
    lib.memory_slot(memory_num).track_wav(track_num) before calling this.

    Args:
        lib: Library for the ROLAND/ directory.
        registry: Schema registry for resolving track fields.
        memory_num: Memory slot (1-99). Must already exist.
        track_num: Track number (1-5).
        src: Path to the source audio file (WAV/FLAC/OGG/etc).

    Returns:
        ImportResult with frame count, duration, and computed loop
        length in measures (None if the track has no tempo set).

    Raises:
        ValueError: If track_num is out of range, memory_num doesn't
            exist, or the source sample rate doesn't match the
            device's native rate (44100 Hz).
    """
    slot = lib.memory_slot(memory_num)
    if not slot.exists:
        raise ValueError(f"Memory {memory_num:03d} does not exist.")

    if not 1 <= track_num <= 5:
        raise ValueError(f"Track number must be 1-5, got {track_num}.")

    data, sr = import_audio(src)

    if sr != DEVICE_SAMPLE_RATE:
        raise ValueError(
            f"Sample rate mismatch: source is {sr} Hz, device requires "
            f"{DEVICE_SAMPLE_RATE} Hz. Please resample your audio to "
            f"{DEVICE_SAMPLE_RATE} Hz before importing."
        )

    wav_dir = lib.wave_dir / f"{memory_num:03d}_{track_num}"
    wav_dir.mkdir(parents=True, exist_ok=True)
    dst_path = wav_dir / f"{memory_num:03d}_{track_num}.WAV"
    wav_write_device(dst_path, data, sr)

    total_samples = data.shape[0]
    measures = None

    rc0 = lib.parse_memory(memory_num)
    mem = Memory(rc0, registry)
    track = mem.track(track_num)
    if track is not None:
        track.set_by_tag("W", 1)  # has_audio = true
        track.set_by_tag("X", total_samples)
        tempo_x10 = track.get_by_tag("U")
        if tempo_x10 and tempo_x10 > 0:
            bpm = tempo_x10 / 10.0
            samples_per_beat = DEVICE_SAMPLE_RATE * 60.0 / bpm
            samples_per_measure = int(samples_per_beat * 4)
            track.set_by_tag("V", samples_per_measure)
            if samples_per_measure > 0:
                measures = round(total_samples / samples_per_measure)
                track.set_by_tag("S", max(1, measures))
        lib.save_memory(memory_num, rc0)

    return ImportResult(
        frames=total_samples,
        duration=total_samples / sr,
        measures=measures,
    )
