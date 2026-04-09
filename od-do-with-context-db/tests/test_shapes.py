"""
Tests for od_do.shapes module.
"""

from od_do.shapes import block, circle, rectangle
from od_do.shapes.base import Block, Circle, Rectangle


def test_block_creation():
    b = block(x0=10, y0=20, width=100, height=50)
    assert b.x == 10
    assert b.y == 20
    assert b.width == 100
    assert b.height == 50


def test_circle_creation():
    c = circle(x0=10, y0=20, radius=30)
    assert c.x == 10
    assert c.y == 20
    assert c.radius == 30


def test_rectangle_creation():
    r = rectangle(x0=5, y0=10, width=50, height=30)
    assert r.x == 5
    assert r.y == 10
    assert r.width == 50
    assert r.height == 30


def test_shape_styling():
    b = block(x0=0, y0=0, fill="#ff0000", stroke="#000000", stroke_width=2)
    assert b.fill == "#ff0000"
    assert b.stroke == "#000000"
    assert b.stroke_width == 2
