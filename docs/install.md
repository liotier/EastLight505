# Install

## With pipx (recommended)

EastLight is an application with command-line and GUI entry points, so
[pipx](https://pipx.pypa.io/) is the recommended way to install it — it
keeps EastLight and its dependencies in an isolated environment while
still putting `eastlight` and `eastlight-gui` on your `PATH`. This also
avoids the `externally-managed-environment` error that a bare `pip
install` hits on modern Debian/Ubuntu/Fedora.

```bash
pipx install "eastlight[gui]"
```

Leave off the `[gui]` extra if you only want the command-line interface:

```bash
pipx install eastlight
```

### Already installed without the GUI extra?

`pipx install eastlight[gui]` refuses to modify an existing install
("already seems to be installed"). Use one of these instead:

```bash
pipx inject eastlight PyQt6
```

```bash
pipx install --force "eastlight[gui]"
```

## With pip

```bash
pip install "eastlight[gui]"
```

Or without the GUI extra:

```bash
pip install eastlight
```

Quoting the extra (`"eastlight[gui]"`) matters on zsh (the default shell
on macOS) — without quotes, `[gui]` is interpreted as a glob pattern and
the command fails with `no matches found`.

## From source

```bash
git clone https://github.com/liotier/EastLightRC-505mk2Librarian.git
cd EastLightRC-505mk2Librarian
pip install -e ".[gui]"
```

## Requirements

- **Python 3.11+**
- **libsndfile** — required by the `soundfile` dependency for audio I/O

### libsndfile

libsndfile is bundled automatically on **Windows** and **macOS** via the `soundfile` pip package.

On **Linux**, install it with your package manager:

=== "Debian / Ubuntu"
    ```bash
    sudo apt install libsndfile1
    ```

=== "Fedora"
    ```bash
    sudo dnf install libsndfile
    ```

=== "Arch"
    ```bash
    sudo pacman -S libsndfile
    ```

## Verify installation

```bash
eastlight --version
eastlight --help
```

You should see the version number and a list of all available commands.

## Launching the GUI

```bash
eastlight gui
```

or, if installed with the `[gui]` extra, the standalone desktop entry point:

```bash
eastlight-gui
```

## Development

```bash
pip install -e ".[dev,gui]"
```

`dev` covers testing and linting; `gui` is needed to run the GUI test
suite (`tests/test_gui.py`) and to work on the GUI code at all.
