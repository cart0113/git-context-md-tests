"""
Tests for od_do.diagram module.
"""

from od_do.diagram import Diagram
from od_do.shapes import block, circle


def test_diagram_creation():
    d = Diagram(width=800, height=600)
    assert d.width == 800
    assert d.height == 600
    assert d.units == "px"


def test_add_shape_to_diagram():
    d = Diagram()
    b = block(x0=10, y0=10, width=100, height=50)
    d.add_shape(b)
    assert len(d.shapes) == 1
    assert d.shapes[0] == b


def test_multiple_shapes():
    d = Diagram()
    b = block(x0=10, y0=10, width=100, height=50)
    c = circle(x0=200, y0=200, radius=30)
    d.add_shape(b)
    d.add_shape(c)
    assert len(d.shapes) == 2
