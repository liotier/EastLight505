# Install

## From PyPI (recommended)

```bash
pip install eastlight
```

## From source

```bash
git clone https://github.com/liotier/EastLightRC-505mk2Librarian.git
cd EastLightRC-505mk2Librarian
pip install -e .
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

## Optional dependencies

For the graphical interface (PyQt6):

```bash
pip install eastlight[gui]
```

Then launch with `eastlight gui`.

For development:

```bash
pip install -e ".[dev,gui]"
```
