---
description:
  Building, installing, running examples, CLI options, documentation site
  workflow, and example file pattern
---

# Development

## Building and installing

```bash
uv-main pip install -e ".[dev,docs]"
# Or: make install
```

## Running examples

```bash
python3 examples/simple_diagram.py --show
python3 examples/simple_diagram.py --output diagram.svg
python3 examples/simple_diagram.py --backend png --output diagram.png
```

## CLI options — `src/od_do/cli.py`

```bash
python3 my_diagram.py                        # Render to output/<Name>.svg
python3 my_diagram.py --show                 # Render and open viewer
python3 my_diagram.py --output file.svg      # Custom output
python3 my_diagram.py --backend png          # Different backend
python3 my_diagram.py --padding 100          # Custom padding (default 50)
python3 my_diagram.py --show-ruler           # Show coordinate ruler
python3 my_diagram.py --show-grid            # Show grid overlay
python3 my_diagram.py --list-diagrams        # List all Diagram classes
python3 my_diagram.py --render-diagram "Name" # Render by name/pattern
```

## Example file pattern

All example files use the CLI interface:

```python
from od_do import cli

if __name__ == "__main__":
    cli()
```

## Documentation site

Docs use bruha (docsify). Build and serve:

```bash
docs/bin/build.sh    # Generate sidebar + config
docs/bin/serve.sh    # Build + launch dev server on port 3000
```

When making API changes, update corresponding docs in `docs/src/` and examples
in `examples/`.
