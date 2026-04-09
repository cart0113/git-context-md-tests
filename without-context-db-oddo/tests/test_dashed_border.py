"""
Tests for DashedBorder shape.
"""

from od_do.diagram import Diagram
from od_do.shapes.base import Block
from od_do.shapes.dashed_border import DashedBorder


def test_dashed_border_bounding_box():
    """A DashedBorder around a Block should expand the bounding box by the margin."""

    class TestDiagram(Diagram):
        def draw(self):
            self.block = Block(
                parent=self,
                width=100,
                height=50,
                fill="#ff0000",
                stroke="#000000",
                stroke_width=1,
                ul=(20, 30),
            )
            self.border = DashedBorder(
                parent=self,
                child=self.block,
                margin=10,
                stroke="#333333",
            )

    d = TestDiagram()

    # Block is at ul=(20, 30) with width=100, height=50
    assert d.block.x == 20
    assert d.block.y == 30
    assert d.block.width == 100
    assert d.block.height == 50

    # DashedBorder should expand by margin=10 on all sides
    assert d.border.x == 10   # 20 - 10
    assert d.border.y == 20   # 30 - 10
    assert d.border.width == 120   # 100 + 2*10
    assert d.border.height == 70   # 50 + 2*10

    # Verify bounding box
    bbox = d.border.bbox
    assert bbox.ur.x == 130   # 10 + 120
    assert bbox.ur.y == 20    # top (smallest y)
    assert bbox.ll.x == 10    # left
    assert bbox.ll.y == 90    # bottom (20 + 70)

    # bounding_box() tuple form
    min_x, min_y, max_x, max_y = d.border.bounding_box()
    assert min_x == 10
    assert min_y == 20
    assert max_x == 130
    assert max_y == 90


def test_dashed_border_child_accessible():
    """The child shape should be accessible via .child."""

    class TestDiagram(Diagram):
        def draw(self):
            self.block = Block(
                parent=self,
                width=80,
                height=40,
                fill="#0000ff",
                stroke=None,
                stroke_width=0,
                ul=(0, 0),
            )
            self.border = DashedBorder(
                parent=self,
                child=self.block,
            )

    d = TestDiagram()

    assert d.border.child is d.block
    assert d.border.child.width == 80
    assert d.border.child.height == 40


def test_dashed_border_child_anchor_points():
    """The child's anchor points should still work through .child."""

    class TestDiagram(Diagram):
        def draw(self):
            self.block = Block(
                parent=self,
                width=100,
                height=50,
                fill="#ff0000",
                stroke="#000000",
                stroke_width=1,
                ul=(20, 30),
            )
            self.border = DashedBorder(
                parent=self,
                child=self.block,
                margin=15,
            )

    d = TestDiagram()

    # Child anchor points should reflect the child, not the border
    child_points = d.border.child.points
    assert child_points.ul.x == 20
    assert child_points.ul.y == 30
    assert child_points.lr.x == 120  # 20 + 100
    assert child_points.lr.y == 80   # 30 + 50


def test_dashed_border_default_margin():
    """Default margin should be 10."""

    class TestDiagram(Diagram):
        def draw(self):
            self.block = Block(
                parent=self,
                width=60,
                height=40,
                fill=None,
                stroke="#000",
                stroke_width=1,
                ul=(50, 50),
            )
            self.border = DashedBorder(
                parent=self,
                child=self.block,
            )

    d = TestDiagram()

    assert d.border.margin == 10
    assert d.border.width == 80   # 60 + 2*10
    assert d.border.height == 60  # 40 + 2*10
