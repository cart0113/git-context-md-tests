"""
Image shape for OD-DO.

Provides an Image shape to embed external images (PNG, SVG, JPG, etc.) into diagrams.

Example:
    from od_do.shapes import image
    from od_do import diagram

    class MyDiagram(diagram.Diagram):
        def draw(self):
            image.Image(
                parent=self,
                file_path="logo.png",
                ll=(100, 200),
                width=150,
                height=100,
            )
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional, Union, Tuple, TYPE_CHECKING

from ..geometry import Point, BBox, Points

if TYPE_CHECKING:
    from ..diagram.base import Diagram

PointLike = Union[Point, Tuple[float, float]]


class Image:
    """An embedded image shape.

    Embeds an external image file (PNG, JPG, SVG, etc.) into the diagram.
    The image can be positioned using corner points (ll, ul, lr, ur) or center.
    """

    def __init__(
        self,
        parent: "Diagram",
        file_path: str,
        width: float,
        height: float,
        ll: Optional[PointLike] = None,
        ul: Optional[PointLike] = None,
        lr: Optional[PointLike] = None,
        ur: Optional[PointLike] = None,
        center: Optional[PointLike] = None,
        opacity: float = 1.0,
        preserve_aspect_ratio: bool = True,
    ):
        self.parent = parent
        self.file_path = Path(file_path)
        self.image_width = width
        self.image_height = height
        self.opacity = opacity
        self.preserve_aspect_ratio = preserve_aspect_ratio

        positions = [ll, ul, lr, ur, center]
        num_positions = sum(1 for p in positions if p is not None)

        if num_positions > 1:
            raise ValueError("Only one of ll, ul, lr, ur, or center can be specified")

        if ll is not None:
            self.x, self.y = self._resolve_ll(ll, width, height)
        elif ul is not None:
            self.x, self.y = self._resolve_ul(ul)
        elif lr is not None:
            self.x, self.y = self._resolve_lr(lr, width, height)
        elif ur is not None:
            self.x, self.y = self._resolve_ur(ur, width)
        elif center is not None:
            self.x, self.y = self._resolve_center(center, width, height)
        else:
            self.x, self.y = 0, 0

        parent.add_shape(self)

    def _resolve_ll(self, ll: PointLike, width: float, height: float) -> Tuple[float, float]:
        pt = Point.resolve_point(ll)
        return (pt.x, pt.y - height)

    def _resolve_ul(self, ul: PointLike) -> Tuple[float, float]:
        pt = Point.resolve_point(ul)
        return (pt.x, pt.y)

    def _resolve_lr(self, lr: PointLike, width: float, height: float) -> Tuple[float, float]:
        pt = Point.resolve_point(lr)
        return (pt.x - width, pt.y - height)

    def _resolve_ur(self, ur: PointLike, width: float) -> Tuple[float, float]:
        pt = Point.resolve_point(ur)
        return (pt.x - width, pt.y)

    def _resolve_center(
        self, center: PointLike, width: float, height: float
    ) -> Tuple[float, float]:
        pt = Point.resolve_point(center)
        return (pt.x - width / 2, pt.y - height / 2)

    @property
    def width(self) -> float:
        return self.image_width

    @property
    def height(self) -> float:
        return self.image_height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self.x, self.y + self.height),
            ur=Point(self.x + self.width, self.y),
        )

    @property
    def points(self) -> Points:
        return Points(self)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def get_mime_type(self) -> str:
        suffix = self.file_path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
        }
        return mime_types.get(suffix, "application/octet-stream")

    def get_base64_data(self) -> str:
        with open(self.file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
