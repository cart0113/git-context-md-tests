"""
Core shapes module for OD-DO.

Basic shapes:
    - Rectangle, Circle, Block, OpenBlock (from base)

Extended shapes:
    - curves: QuadraticBezier, CubicBezier, Arc, SemiCircle
    - polygon: RegularPolygon, Triangle, Pentagon, Hexagon, Octagon, Star
    - ellipse: Ellipse
    - annotations: DimensionLine, LeaderLine, Callout
    - flowchart: Diamond, Parallelogram, Document, Cylinder, Cloud, Terminator
    - text: Text, TextBox, Label
    - table: Table, EntityTable, KeyValueTable
"""

from .base import Rectangle, Circle, Block, OpenBlock

from . import curves
from . import polygon
from . import ellipse
from . import annotations
from . import flowchart
from . import text
from . import table
from . import dashed_border
