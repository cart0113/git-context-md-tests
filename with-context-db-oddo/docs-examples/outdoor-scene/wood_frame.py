"""
Wood Frame - A wiggly organic wood-like frame for the outdoor scene.

The frame has:
- Irregular, organic edges (not straight lines)
- Wood grain texture
- Natural wood colors with variation
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli, colors, diagram
from od_do.shapes import curves

random.seed(42)


FRAME_WIDTH = 800
FRAME_HEIGHT = 600
BORDER_THICKNESS = 35
INNER_MARGIN = 8


WOOD_BASE = colors.Color("#A87B3A")
WOOD_LIGHT = colors.Color("#C4A060")
WOOD_DARK = colors.Color("#6B5030")
WOOD_GRAIN = colors.Color("#7A6040")


def generate_wiggly_path(points, wiggle_amplitude, wiggle_frequency):
    """Generate a wiggly SVG path through a series of points."""
    if len(points) < 2:
        return ""

    path = f"M {points[0][0]},{points[0][1]}"

    for i in range(1, len(points)):
        x1, y1 = points[i - 1]
        x2, y2 = points[i]

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        offset = math.sin(i * wiggle_frequency) * wiggle_amplitude
        offset += random.uniform(-wiggle_amplitude * 0.3, wiggle_amplitude * 0.3)

        if abs(x2 - x1) > abs(y2 - y1):
            ctrl_x = mid_x
            ctrl_y = mid_y + offset
        else:
            ctrl_x = mid_x + offset
            ctrl_y = mid_y

        path += f" Q {ctrl_x},{ctrl_y} {x2},{y2}"

    return path


class WoodFrame(diagram.Diagram):
    """Organic wiggly wood frame."""

    render_padding = 0

    def draw(self):
        self._draw_frame_with_hole()
        self._draw_grain_texture()
        self._draw_knots()

    def _draw_frame_with_hole(self):
        self._draw_border_strip("top")
        self._draw_border_strip("bottom")
        self._draw_border_strip("left")
        self._draw_border_strip("right")

    def _draw_border_strip(self, side):
        num_points = 40

        if side == "top":
            outer_points = [(i / (num_points - 1) * FRAME_WIDTH, random.uniform(-3, 3)) for i in range(num_points)]
            inner_points = [(i / (num_points - 1) * FRAME_WIDTH, BORDER_THICKNESS + random.uniform(-2, 2)) for i in range(num_points - 1, -1, -1)]
        elif side == "bottom":
            outer_points = [(i / (num_points - 1) * FRAME_WIDTH, FRAME_HEIGHT + random.uniform(-3, 3)) for i in range(num_points)]
            inner_points = [(i / (num_points - 1) * FRAME_WIDTH, FRAME_HEIGHT - BORDER_THICKNESS + random.uniform(-2, 2)) for i in range(num_points - 1, -1, -1)]
        elif side == "left":
            outer_points = [(random.uniform(-3, 3), i / (num_points - 1) * FRAME_HEIGHT) for i in range(num_points)]
            inner_points = [(BORDER_THICKNESS + random.uniform(-2, 2), i / (num_points - 1) * FRAME_HEIGHT) for i in range(num_points - 1, -1, -1)]
        else:
            outer_points = [(FRAME_WIDTH + random.uniform(-3, 3), i / (num_points - 1) * FRAME_HEIGHT) for i in range(num_points)]
            inner_points = [(FRAME_WIDTH - BORDER_THICKNESS + random.uniform(-2, 2), i / (num_points - 1) * FRAME_HEIGHT) for i in range(num_points - 1, -1, -1)]

        all_points = outer_points + inner_points
        path = generate_wiggly_path(all_points, 3, 0.8)
        path += " Z"

        curves.BezierPath(
            parent=self,
            d=path,
            stroke=WOOD_DARK,
            stroke_width=2,
            fill=WOOD_BASE,
        )

    def _draw_grain_texture(self):
        num_grains = 300

        for _ in range(num_grains):
            edge = random.choice(["top", "bottom", "left", "right"])

            if edge == "top":
                x = random.uniform(10, FRAME_WIDTH - 10)
                y = random.uniform(5, BORDER_THICKNESS - 5)
                angle = random.uniform(-0.2, 0.2)
                length = random.uniform(20, 50)
            elif edge == "bottom":
                x = random.uniform(10, FRAME_WIDTH - 10)
                y = random.uniform(FRAME_HEIGHT - BORDER_THICKNESS + 5, FRAME_HEIGHT - 5)
                angle = random.uniform(-0.2, 0.2)
                length = random.uniform(20, 50)
            elif edge == "left":
                x = random.uniform(5, BORDER_THICKNESS - 5)
                y = random.uniform(BORDER_THICKNESS + 10, FRAME_HEIGHT - BORDER_THICKNESS - 10)
                angle = random.uniform(math.pi / 2 - 0.2, math.pi / 2 + 0.2)
                length = random.uniform(20, 50)
            else:
                x = random.uniform(FRAME_WIDTH - BORDER_THICKNESS + 5, FRAME_WIDTH - 5)
                y = random.uniform(BORDER_THICKNESS + 10, FRAME_HEIGHT - BORDER_THICKNESS - 10)
                angle = random.uniform(math.pi / 2 - 0.2, math.pi / 2 + 0.2)
                length = random.uniform(20, 50)

            end_x = x + length * math.cos(angle)
            end_y = y + length * math.sin(angle)

            curve_offset = random.uniform(-5, 5)
            ctrl_x = (x + end_x) / 2 + curve_offset * math.sin(angle)
            ctrl_y = (y + end_y) / 2 - curve_offset * math.cos(angle)

            grain_color = WOOD_GRAIN.alpha(random.uniform(0.2, 0.5))
            if random.random() < 0.3:
                grain_color = WOOD_DARK.alpha(random.uniform(0.15, 0.35))
            elif random.random() < 0.3:
                grain_color = WOOD_LIGHT.alpha(random.uniform(0.2, 0.4))

            curves.QuadraticBezier(
                parent=self,
                start=(x, y),
                control=(ctrl_x, ctrl_y),
                end=(end_x, end_y),
                stroke=grain_color,
                stroke_width=random.uniform(1.5, 3.5),
                fill=None,
            )

    def _draw_knots(self):
        knot_positions = [
            (BORDER_THICKNESS / 2, FRAME_HEIGHT * 0.3),
            (FRAME_WIDTH - BORDER_THICKNESS / 2, FRAME_HEIGHT * 0.6),
            (FRAME_WIDTH * 0.25, BORDER_THICKNESS / 2),
            (FRAME_WIDTH * 0.7, FRAME_HEIGHT - BORDER_THICKNESS / 2),
        ]

        for kx, ky in knot_positions:
            if random.random() < 0.7:
                self._draw_knot(kx, ky)

    def _draw_knot(self, cx, cy):
        num_rings = random.randint(3, 5)
        base_radius = random.uniform(3, 6)

        for i in range(num_rings):
            radius = base_radius + i * 2
            ring_color = WOOD_DARK.darken(0.1 * i).alpha(0.6 - i * 0.1)

            num_points = 12
            points = []
            for j in range(num_points + 1):
                angle = (j / num_points) * 2 * math.pi
                wobble = random.uniform(-1, 1)
                r = radius + wobble
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                points.append((x, y))

            path = generate_wiggly_path(points, 0.5, 2.0)
            curves.BezierPath(
                parent=self,
                d=path,
                stroke=ring_color,
                stroke_width=random.uniform(0.5, 1.0),
                fill=None,
            )

        curves.BezierPath(
            parent=self,
            d=f"M {cx-2},{cy} A 2,2 0 1,1 {cx+2},{cy} A 2,2 0 1,1 {cx-2},{cy}",
            stroke=None,
            stroke_width=0,
            fill=WOOD_DARK.darken(0.3),
        )


if __name__ == "__main__":
    cli()
