"""Shared test fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def dump_dir() -> Path:
    """Path to a real device dump's ROLAND/DATA directory, if available.

    Controlled by the EASTLIGHT_DUMP_DIR env var, which should point at
    a directory containing an extracted ROLAND/ tree (as produced by
    `tar -xzf rc0-files.tar.gz`). Defaults to /tmp/rc505-dump for local
    development. Skips the test if the dump isn't present.
    """
    base = Path(os.environ.get("EASTLIGHT_DUMP_DIR", "/tmp/rc505-dump"))
    d = base / "ROLAND" / "DATA"
    if not d.exists():
        pytest.skip("Device dump not available (set EASTLIGHT_DUMP_DIR)")
    return d


@pytest.fixture
def sample_rc0_content() -> str:
    """Minimal valid RC0 file content for testing."""
    return '''<?xml version="1.0" encoding="utf-8"?>
<database name="RC-505MK2" revision="0">
<mem id="0">
<NAME>
<A>77</A>
<B>101</B>
<C>109</C>
<D>111</D>
<E>114</E>
<F>121</F>
<G>32</G>
<H>49</H>
<I>32</I>
<J>32</J>
<K>32</K>
<L>32</L>
</NAME>
<TRACK1>
<A>0</A>
<B>0</B>
<C>50</C>
<D>100</D>
<E>0</E>
<F>0</F>
<G>0</G>
<H>0</H>
<I>0</I>
<J>5</J>
<K>0</K>
<L>1</L>
<M>0</M>
<N>1</N>
<O>1</O>
<P>0</P>
<Q>127</Q>
<R>0</R>
<S>8</S>
<T>0</T>
<U>700</U>
<V>151200</V>
<W>1</W>
<X>1209600</X>
<Y>1</Y>
</TRACK1>
<TRACK2>
<A>0</A>
<B>0</B>
<C>50</C>
<D>100</D>
<E>0</E>
<F>0</F>
<G>0</G>
<H>1</H>
<I>0</I>
<J>0</J>
<K>0</K>
<L>1</L>
<M>0</M>
<N>1</N>
<O>1</O>
<P>0</P>
<Q>127</Q>
<R>0</R>
<S>0</S>
<T>0</T>
<U>1200</U>
<V>0</V>
<W>0</W>
<X>0</X>
<Y>2</Y>
</TRACK2>
<MASTER>
<A>100</A>
<B>0</B>
</MASTER>
</mem>
<ifx id="0">
<SETUP>
<A>0</A>
</SETUP>
</ifx>
<tfx id="0">
<SETUP>
<A>0</A>
</SETUP>
</tfx>
</database>
<count>0013</count>
'''


@pytest.fixture
def sample_rc0_path(tmp_path: Path, sample_rc0_content: str) -> Path:
    """Write sample RC0 to a temp file and return its path."""
    path = tmp_path / "MEMORY001A.RC0"
    path.write_text(sample_rc0_content, encoding="utf-8")
    return path


@pytest.fixture
def two_chain_rc0_content() -> str:
    """RC0 content with a subslot ('AA') and effect section ('AA_LPF')
    present in BOTH <ifx> and <tfx> with different values in each chain.

    Real device memories have ~1000 identically-named sections shared
    between the ifx and tfx elements (AA, AA_LPF, ..., DD_REVERB, ...).
    This fixture exists specifically to catch section-name collisions
    between the two chains, which the minimal sample_rc0_content fixture
    (a single shared SETUP section) doesn't exercise.
    """
    return '''<?xml version="1.0" encoding="utf-8"?>
<database name="RC-505MK2" revision="0">
<mem id="0">
<NAME>
<A>70</A>
<B>88</B>
<C>32</C>
<D>80</D>
<E>97</E>
<F>116</F>
<G>99</G>
<H>104</H>
<I>32</I>
<J>32</J>
<K>32</K>
<L>32</L>
</NAME>
<MASTER>
<A>100</A>
<B>0</B>
</MASTER>
</mem>
<ifx id="0">
<SETUP>
<A>0</A>
</SETUP>
<AA>
<A>1</A>
<B>0</B>
<C>35</C>
<D>0</D>
</AA>
<AA_LPF>
<A>3</A>
<B>50</B>
<C>50</C>
<D>50</D>
<E>0</E>
</AA_LPF>
</ifx>
<tfx id="0">
<SETUP>
<A>0</A>
</SETUP>
<AA>
<A>1</A>
<B>0</B>
<C>49</C>
<D>0</D>
</AA>
<AA_LPF>
<A>9</A>
<B>90</B>
<C>90</C>
<D>90</D>
<E>1</E>
</AA_LPF>
</tfx>
</database>
<count>0013</count>
'''


@pytest.fixture
def two_chain_rc0_path(tmp_path: Path, two_chain_rc0_content: str) -> Path:
    """Write two_chain_rc0_content to a temp file and return its path."""
    path = tmp_path / "MEMORY001A.RC0"
    path.write_text(two_chain_rc0_content, encoding="utf-8")
    return path
