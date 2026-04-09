# Configuration

OD-DO uses a configuration file located at `~/.od-do-config` to customize
behavior.

## Configuration File Location

The configuration file should be placed at:

```bash
~/.od-do-config
```

This file uses TOML format for configuration options.

## Configuration Options

### svg_viewer

The command to use for viewing SVG files when using `--show`.

**Default:** `open` (macOS), `xdg-open` (Linux), `start` (Windows)

**Example:**

```toml
svg_viewer = "firefox"
```

### png_viewer

The command to use for viewing PNG files when using `--show`.

**Default:** `open` (macOS), `xdg-open` (Linux), `start` (Windows)

**Example:**

```toml
png_viewer = "gimp"
```

### drawio_viewer

The command to use for viewing Draw.io files when using `--show`.

**Default:** `open` (macOS), `xdg-open` (Linux), `start` (Windows)

**Example:**

```toml
drawio_viewer = "/Applications/draw.io.app/Contents/MacOS/draw.io"
```

### default_backend

The default backend to use when rendering diagrams.

**Default:** `svg`

**Options:** `svg`, `png`, `drawio`

**Example:**

```toml
default_backend = "svg"
```

### default_width

The default width for diagrams in pixels.

**Default:** `800`

**Example:**

```toml
default_width = 1024
```

### default_height

The default height for diagrams in pixels.

**Default:** `600`

**Example:**

```toml
default_height = 768
```

## Example Configuration File

```toml
# ~/.od-do-config

# Viewer commands
svg_viewer = "firefox"
png_viewer = "open"
drawio_viewer = "/Applications/draw.io.app/Contents/MacOS/draw.io"

# Default rendering options
default_backend = "svg"
default_width = 1024
default_height = 768
```

## Platform-Specific Defaults

OD-DO automatically selects appropriate defaults based on your operating system:

### macOS

```toml
svg_viewer = "open"
png_viewer = "open"
drawio_viewer = "open"
```

### Linux

```toml
svg_viewer = "xdg-open"
png_viewer = "xdg-open"
drawio_viewer = "xdg-open"
```

### Windows

```toml
svg_viewer = "start"
png_viewer = "start"
drawio_viewer = "start"
```

## Using Configuration in CLI

The configuration file affects the behavior of the `--show` flag:

```bash
# Uses the configured svg_viewer
python3 my_diagram.py --show --backend svg

# Uses the configured png_viewer
python3 my_diagram.py --show --backend png
```

## Configuration Priority

Configuration values are resolved in the following order (highest to lowest
priority):

1. Command-line arguments
2. Configuration file (`~/.od-do-config`)
3. Platform-specific defaults

## Creating Your Configuration

To create a configuration file:

```bash
# Create the file
touch ~/.od-do-config

# Edit with your preferred editor
nano ~/.od-do-config
```

Then add your desired configuration options in TOML format.
