"""
PNG backend for OD-DO.
"""

from typing import List
from .base import Backend
from ...shapes.base import Shape, Rectangle, Circle


class PNGBackend(Backend):
    def render(self, shapes: List[Shape], output_path: str, **kwargs):
        from PIL import Image, ImageDraw

        width = kwargs.get("width", 800)
        height = kwargs.get("height", 600)
        background = kwargs.get("background", "white")

        img = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(img)

        for shape in shapes:
            self._draw_shape(draw, shape)

        img.save(output_path)

    def _draw_shape(self, draw, shape: Shape):
        if isinstance(shape, Circle):
            self._draw_circle(draw, shape)
        elif isinstance(shape, Rectangle):
            self._draw_rectangle(draw, shape)

    def _draw_rectangle(self, draw, rect: Rectangle):
        x1, y1 = rect.x, rect.y
        x2, y2 = rect.x + rect.width, rect.y + rect.height

        fill = rect.fill
        outline = rect.stroke or "black"
        width = int(rect.stroke_width)

        draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline, width=width)

    def _draw_circle(self, draw, circle: Circle):
        x1 = circle.x
        y1 = circle.y
        x2 = circle.x + circle.radius * 2
        y2 = circle.y + circle.radius * 2

        fill = circle.fill
        outline = circle.stroke or "black"
        width = int(circle.stroke_width)

        draw.ellipse([x1, y1, x2, y2], fill=fill, outline=outline, width=width)
