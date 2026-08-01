"""Tests for the typed data model."""

from __future__ import annotations

from pathlib import Path

import pytest

from eastlight.core.model import FieldChange, Memory
from eastlight.core.parser import parse_memory_file
from eastlight.core.schema import SchemaRegistry


@pytest.fixture
def registry() -> SchemaRegistry:
    schema_dir = Path(__file__).parent.parent / "src" / "eastlight" / "schema"
    reg = SchemaRegistry()
    reg.load_all(schema_dir)
    return reg


class TestMemory:
    def test_name_decoding(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        assert mem.name == "Memory 1"

    def test_track_access(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        assert track1 is not None
        assert track1.get_by_name("pan") == 50
        assert track1.get_by_name("play_level") == 100
        assert track1.get_by_name("tempo_x10") == 700

    def test_track_by_tag(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        assert track1.get_by_tag("C") == 50
        assert track1.get_by_tag("U") == 700

    def test_as_dict(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        d = track1.as_dict()
        assert d["pan"] == 50
        assert d["tempo_x10"] == 700
        assert d["has_audio"] == 1

    def test_set_by_name(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        track1.set_by_name("pan", 75)
        assert track1.get_by_name("pan") == 75
        assert track1.get_by_tag("C") == 75

    def test_set_validates_range(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        with pytest.raises(ValueError, match="out of range"):
            track1.set_by_name("pan", 200)

    def test_set_rejects_read_only(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        with pytest.raises(ValueError, match="read-only"):
            track1.set_by_name("has_audio", 0)

    def test_section_names(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        names = mem.section_names
        assert "NAME" in names
        assert "TRACK1" in names
        assert "MASTER" in names
        # SETUP lives in <ifx>/<tfx>, not <mem> — reachable via
        # fx_section(), not section_names (see test_fx_sections_ifx_tfx_distinct
        # and test_section_names_excludes_fx_sections below for why these
        # namespaces are kept separate).
        assert "SETUP" not in names
        assert mem.fx_section("ifx", "SETUP") is not None
        assert mem.fx_section("tfx", "SETUP") is not None

    def test_fx_sections_ifx_tfx_distinct(
        self, two_chain_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        """ifx and tfx share ~1000 identical section names on a real device
        (AA, AA_LPF, ...). Memory must keep them in separate namespaces
        rather than letting the later element silently overwrite the
        earlier one under the same bare name."""
        rc0 = parse_memory_file(two_chain_rc0_path)
        mem = Memory(rc0, registry)

        ifx_aa = mem.fx_section("ifx", "AA")
        tfx_aa = mem.fx_section("tfx", "AA")
        assert ifx_aa is not None
        assert tfx_aa is not None
        assert ifx_aa is not tfx_aa
        assert ifx_aa.get_by_tag("C") == 35  # ifx fx_type, from the fixture
        assert tfx_aa.get_by_tag("C") == 49  # tfx fx_type, from the fixture

        ifx_lpf = mem.fx_section("ifx", "AA_LPF")
        tfx_lpf = mem.fx_section("tfx", "AA_LPF")
        assert ifx_lpf is not None
        assert tfx_lpf is not None
        assert ifx_lpf.get_by_tag("A") == 3
        assert tfx_lpf.get_by_tag("A") == 9

    def test_fx_section_missing_chain_or_name(
        self, two_chain_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(two_chain_rc0_path)
        mem = Memory(rc0, registry)
        assert mem.fx_section("ifx", "NONEXISTENT") is None
        assert mem.fx_section("tfx", "AA") is not None

    def test_fx_section_names_scoped_to_chain(
        self, two_chain_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(two_chain_rc0_path)
        mem = Memory(rc0, registry)
        ifx_names = mem.fx_section_names("ifx")
        tfx_names = mem.fx_section_names("tfx")
        assert set(ifx_names) == {"SETUP", "AA", "AA_LPF"}
        assert set(tfx_names) == {"SETUP", "AA", "AA_LPF"}

    def test_section_names_excludes_fx_sections(
        self, two_chain_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        """Memory.section_names must only reflect the mem element — FX
        sections live in a separate namespace and are never ambiguous
        with mem-level sections, but must not leak into this list either
        (a caller iterating section_names to build e.g. a template export
        should not accidentally pick up one chain's copy of a shared
        section name and mislabel it as mem-level data)."""
        rc0 = parse_memory_file(two_chain_rc0_path)
        mem = Memory(rc0, registry)
        assert set(mem.section_names) == {"NAME", "MASTER"}
        assert "AA" not in mem.section_names
        assert "SETUP" not in mem.section_names

    def test_master_schema_resolution(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        master = mem.section("MASTER")
        assert master is not None
        assert master.get_by_name("tempo_x10") is not None
        d = master.as_dict()
        assert "tempo_x10" in d
        assert "samples_per_measure" in d


class TestSchemaResolution:
    """Schema resolution tests against real device dump."""

    @pytest.fixture
    def real_mem(self, dump_dir: Path, registry: SchemaRegistry) -> Memory:
        rc0 = parse_memory_file(dump_dir / "MEMORY001A.RC0")
        return Memory(rc0, registry)

    def test_rec_schema(self, real_mem: Memory) -> None:
        rec = real_mem.section("REC")
        assert rec is not None
        d = rec.as_dict()
        assert "rec_action" in d
        assert "quantize" in d
        assert "auto_rec_sens" in d

    def test_eq_schema(self, real_mem: Memory) -> None:
        eq = real_mem.section("EQ_MIC1")
        assert eq is not None
        d = eq.as_dict()
        assert "sw" in d
        assert "lo_gain" in d
        assert "hi_mid_freq" in d

    def test_assign_schema(self, real_mem: Memory) -> None:
        assign1 = real_mem.section("ASSIGN1")
        assert assign1 is not None
        d = assign1.as_dict()
        assert "sw" in d
        assert "source" in d
        assert "target" in d

    def test_master_schema(self, real_mem: Memory) -> None:
        master = real_mem.section("MASTER")
        assert master is not None
        d = master.as_dict()
        assert "tempo_x10" in d
        assert d["tempo_x10"] == 700

    def test_play_schema(self, real_mem: Memory) -> None:
        play = real_mem.section("PLAY")
        assert play is not None
        d = play.as_dict()
        assert "single_play_change" in d
        assert "fade_time_in" in d

    def test_rhythm_schema(self, real_mem: Memory) -> None:
        rhythm = real_mem.section("RHYTHM")
        assert rhythm is not None
        d = rhythm.as_dict()
        assert "pattern" in d
        assert "variation" in d

    def test_mixer_schema(self, real_mem: Memory) -> None:
        mixer = real_mem.section("MIXER")
        assert mixer is not None
        d = mixer.as_dict()
        assert "mic1_level" in d
        assert "master_out" in d

    def test_routing_schema(self, real_mem: Memory) -> None:
        routing = real_mem.section("ROUTING")
        assert routing is not None
        d = routing.as_dict()
        assert "main_l_tracks" in d
        assert "phones_monitor" in d

    def test_output_schema(self, real_mem: Memory) -> None:
        output = real_mem.section("OUTPUT")
        assert output is not None
        d = output.as_dict()
        assert "output_knob" in d
        assert "stereo_link_main" in d

    def test_input_schema(self, real_mem: Memory) -> None:
        inp = real_mem.section("INPUT")
        assert inp is not None
        d = inp.as_dict()
        assert "gain_mic1" in d

    def test_master_fx_schema(self, real_mem: Memory) -> None:
        mfx = real_mem.section("MASTER_FX")
        assert mfx is not None
        d = mfx.as_dict()
        assert "comp" in d
        assert "reverb" in d


class TestUndoRedo:
    def test_undo_reverts_value(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        assert track1.get_by_name("pan") == 50
        track1.set_by_name("pan", 75)
        assert track1.get_by_name("pan") == 75
        change = mem.undo()
        assert change is not None
        assert change.old_value == 50
        assert change.new_value == 75
        assert track1.get_by_name("pan") == 50

    def test_redo_reapplies_value(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        track1.set_by_name("pan", 75)
        mem.undo()
        assert track1.get_by_name("pan") == 50
        change = mem.redo()
        assert change is not None
        assert track1.get_by_name("pan") == 75

    def test_undo_empty_returns_none(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        assert mem.undo() is None

    def test_new_change_clears_redo(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        track1.set_by_name("pan", 75)
        mem.undo()
        assert mem.undo_stack.can_redo
        track1.set_by_name("pan", 60)  # new change clears redo
        assert not mem.undo_stack.can_redo

    def test_multiple_undo(self, sample_rc0_path: Path, registry: SchemaRegistry) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        track1.set_by_name("pan", 60)
        track1.set_by_name("pan", 70)
        track1.set_by_name("pan", 80)
        assert track1.get_by_name("pan") == 80
        mem.undo()
        assert track1.get_by_name("pan") == 70
        mem.undo()
        assert track1.get_by_name("pan") == 60
        mem.undo()
        assert track1.get_by_name("pan") == 50


class TestChangeListener:
    def test_listener_receives_changes(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        changes: list[FieldChange] = []
        track1.add_listener(changes.append)
        track1.set_by_name("pan", 75)
        assert len(changes) == 1
        assert changes[0].param_name == "pan"
        assert changes[0].old_value == 50
        assert changes[0].new_value == 75

    def test_remove_listener(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        changes: list[FieldChange] = []
        track1.add_listener(changes.append)
        track1.set_by_name("pan", 75)
        track1.remove_listener(changes.append)
        track1.set_by_name("pan", 80)
        assert len(changes) == 1  # only the first change

    def test_undo_notifies_listener(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        """Memory.undo() must notify listeners, not just mutate raw data.

        A GUI widget bound via add_listener() needs to hear about the
        reversal so it can update its display; if undo() bypasses the
        listener path, the widget silently goes stale while the
        underlying data has actually changed.
        """
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        changes: list[FieldChange] = []
        track1.add_listener(changes.append)

        track1.set_by_name("pan", 75)
        assert len(changes) == 1

        mem.undo()
        assert len(changes) == 2, "undo() did not notify the listener"
        assert changes[1].param_name == "pan"
        assert changes[1].old_value == 75
        assert changes[1].new_value == 50
        assert track1.get_by_name("pan") == 50

    def test_redo_notifies_listener(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        changes: list[FieldChange] = []

        track1.set_by_name("pan", 75)
        mem.undo()
        track1.add_listener(changes.append)

        mem.redo()
        assert len(changes) == 1, "redo() did not notify the listener"
        assert changes[0].old_value == 50
        assert changes[0].new_value == 75
        assert track1.get_by_name("pan") == 75

    def test_undo_does_not_push_new_undo_entry(
        self, sample_rc0_path: Path, registry: SchemaRegistry
    ) -> None:
        """undo() must notify listeners without re-pushing the reversed
        change onto the undo stack (that would make undo un-undoable and
        corrupt the stack depth)."""
        rc0 = parse_memory_file(sample_rc0_path)
        mem = Memory(rc0, registry)
        track1 = mem.track(1)
        track1.set_by_name("pan", 75)
        assert mem.undo_stack.can_undo
        mem.undo()
        assert not mem.undo_stack.can_undo
        assert mem.undo_stack.can_redo
