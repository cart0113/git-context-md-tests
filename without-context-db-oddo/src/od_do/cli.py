"""
CLI for OD-DO.
"""

import sys
import subprocess
import importlib.util
import inspect
import re
from pathlib import Path
import click

from .config import get_config


@click.command()
@click.option(
    "--render-diagram",
    help="Name or regex pattern (case-insensitive) of diagram class(es) to render",
)
@click.option("--list-diagrams", is_flag=True, help="List all diagram classes in the file and exit")
@click.option("--kwarg", multiple=True, help="Keyword arguments in format key=value")
@click.option("--show-ruler", is_flag=True, help="Show ruler on the outside of the diagram")
@click.option("--show-grid", is_flag=True, help="Show grid overlay on the diagram")
@click.option("--output", help="Output file path")
@click.option(
    "--backend",
    type=click.Choice(["svg", "png", "drawio"]),
    default="svg",
    help="Backend to use for rendering",
)
@click.option("--show", is_flag=True, help="Show the diagram in viewer")
@click.option("--padding", type=float, default=None, help="Padding around diagram in pixels")
def cli(
    render_diagram, list_diagrams, kwarg, show_ruler, show_grid, output, backend, show, padding
):
    calling_file = Path(sys.argv[0]).resolve()
    click.echo(f"Loading {calling_file.name}...")

    spec = importlib.util.spec_from_file_location("user_module", calling_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    from od_do.diagram import Diagram

    def is_user_defined_diagram(cls):
        """Check if this is a Diagram class defined in the user's file.

        Returns True if the class:
        1. Is a subclass of Diagram (but not Diagram itself)
        2. Was defined in the user's module (not imported from elsewhere)
        """
        if not issubclass(cls, Diagram) or cls is Diagram:
            return False
        # Check if class was defined in the user's module
        return cls.__module__ == "user_module"

    diagram_class_set = {
        name
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if is_user_defined_diagram(obj)
    }

    source_text = calling_file.read_text()
    class_pattern = re.compile(r"^class\s+(\w+)\s*[\(:]", re.MULTILINE)
    source_order = [m.group(1) for m in class_pattern.finditer(source_text)]
    diagram_classes = [name for name in source_order if name in diagram_class_set]

    if list_diagrams:
        if len(diagram_classes) == 0:
            click.echo("No Diagram classes found in file")
        else:
            click.echo(f"Found {len(diagram_classes)} diagram(s):")
            for name in diagram_classes:
                click.echo(f"  {name}")
        return

    if not render_diagram:
        if len(diagram_classes) == 0:
            click.echo("No Diagram classes found in file")
            return
        elif len(diagram_classes) == 1:
            matched_classes = [diagram_classes[0]]
            click.echo(f"Found 1 diagram, rendering: {diagram_classes[0]}")
        else:
            matched_classes = [diagram_classes[-1]]
            click.echo(
                f"Found {len(diagram_classes)} diagrams, rendering last: {diagram_classes[-1]}"
            )
    else:
        pattern = re.compile(render_diagram, re.IGNORECASE)
        matched_classes = [name for name in diagram_classes if pattern.search(name)]
        if not matched_classes:
            click.echo(f"No diagram matching '{render_diagram}' found. Valid diagrams:")
            for name in diagram_classes:
                click.echo(f"  {name}")
            return
        click.echo(
            f"Found {len(diagram_classes)} diagrams, matched {len(matched_classes)}: {', '.join(matched_classes)}"
        )

    kwargs = {}
    if kwarg:
        for kv in kwarg:
            key, value = kv.split("=", 1)
            kwargs[key] = value

    render_kwargs = {}
    if padding is not None:
        render_kwargs["padding"] = padding
    if show_ruler:
        render_kwargs["show_ruler"] = True
    if show_grid:
        render_kwargs["show_grid"] = True

    output_paths = []
    for class_name in matched_classes:
        diagram_class = getattr(module, class_name)
        diagram_instance = diagram_class(**kwargs)

        if output and len(matched_classes) == 1:
            output_path = Path(output)
        else:
            output_dir = calling_file.parent / "output"
            output_path = output_dir / f"{class_name}.{backend}"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        diagram_instance.render(str(output_path), backend=backend, **render_kwargs)
        click.echo(f"Saved: {output_path}")
        output_paths.append(output_path)

    if show:
        config = get_config()
        viewer = config["svg_viewer"]
        for output_path in output_paths:
            if isinstance(viewer, list):
                cmd = viewer + [str(output_path)]
            else:
                cmd = [viewer, str(output_path)]
            click.echo(f"Opening in {cmd[0]}...")
            subprocess.run(cmd)
