"""
Grass Text - "od-do" spelled out with grass-like elements.

The letters are formed from thousands of small grass blades in
autumnal colors: reddish, brown, orange, and dark blue.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli, colors, diagram
from od_do.shapes import curves

random.seed(42)


GRASS_COLORS = [
    colors.Color("#8B2500"),
    colors.Color("#A0522D"),
    colors.Color("#CD853F"),
    colors.Color("#D2691E"),
    colors.Color("#B8860B"),
    colors.Color("#DAA520"),
    colors.Color("#FF8C00"),
    colors.Color("#FF6347"),
    colors.Color("#CC5500"),
    colors.Color("#8B4513"),
    colors.Color("#A52A2A"),
    colors.Color("#654321"),
    colors.Color("#1E3A5F"),
    colors.Color("#2C4A6E"),
    colors.Color("#1B4F72"),
    colors.Color("#154360"),
]


def get_letter_o_points(cx, cy, outer_r, inner_r, density):
    """Generate points that fill a letter 'o' (ring shape)."""
    points = []
    for _ in range(density):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(inner_r, outer_r)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    return points


def get_letter_d_points(x, y, width, height, thickness, density):
    """Generate points that fill a lowercase 'd' (bowl on left, tall stem on right)."""
    points = []

    ascender_height = height * 0.4
    stem_x = x + width - thickness

    for _ in range(density // 2):
        px = stem_x + random.uniform(0, thickness)
        py = y + random.uniform(-ascender_height, height)
        points.append((px, py))

    bowl_cx = x + width - thickness
    bowl_cy = y + height * 0.5
    bowl_outer_r = height * 0.5
    bowl_inner_r = bowl_outer_r - thickness

    for _ in range(density // 2):
        angle = random.uniform(math.pi / 2, 3 * math.pi / 2)
        r = random.uniform(bowl_inner_r, bowl_outer_r)
        px = bowl_cx + r * math.cos(angle)
        py = bowl_cy + r * math.sin(angle)
        points.append((px, py))

    return points


def get_letter_dash_points(x, y, width, height, density):
    """Generate points that fill a dash/hyphen."""
    points = []
    for _ in range(density):
        px = x + random.uniform(0, width)
        py = y + random.uniform(0, height)
        points.append((px, py))
    return points


class GrassText(diagram.Diagram):
    """Text 'od-do' made from thousands of grass-like elements."""

    render_padding = 10

    def draw(self):
        base_x = 20
        base_y = 10
        letter_height = 50
        letter_width = 38
        thickness = 12
        spacing = 15
        density_per_letter = 800

        o1_points = get_letter_o_points(
            cx=base_x + letter_width / 2,
            cy=base_y + letter_height / 2,
            outer_r=letter_height / 2,
            inner_r=letter_height / 2 - thickness,
            density=density_per_letter,
        )

        d1_x = base_x + letter_width + spacing
        d1_points = get_letter_d_points(
            x=d1_x,
            y=base_y,
            width=letter_width,
            height=letter_height,
            thickness=thickness,
            density=density_per_letter,
        )

        dash_x = d1_x + letter_width + spacing
        dash_y = base_y + letter_height * 0.4
        dash_points = get_letter_dash_points(
            x=dash_x,
            y=dash_y,
            width=letter_width * 0.5,
            height=thickness,
            density=density_per_letter // 3,
        )

        d2_x = dash_x + letter_width * 0.5 + spacing
        d2_points = get_letter_d_points(
            x=d2_x,
            y=base_y,
            width=letter_width,
            height=letter_height,
            thickness=thickness,
            density=density_per_letter,
        )

        o2_points = get_letter_o_points(
            cx=d2_x + letter_width + spacing + letter_width / 2,
            cy=base_y + letter_height / 2,
            outer_r=letter_height / 2,
            inner_r=letter_height / 2 - thickness,
            density=density_per_letter,
        )

        all_points = o1_points + d1_points + dash_points + d2_points + o2_points

        for x, y in all_points:
            self._draw_grass_blade(x, y)

    def _draw_grass_blade(self, x, y):
        grass_color = random.choice(GRASS_COLORS)
        if random.random() < 0.3:
            grass_color = grass_color.lighten(random.uniform(0.05, 0.2))
        elif random.random() < 0.3:
            grass_color = grass_color.darken(random.uniform(0.05, 0.15))

        blade_height = random.uniform(4, 12)
        blade_curve = random.uniform(-6, 6)

        end_x = x + blade_curve
        end_y = y - blade_height

        ctrl_x = x + blade_curve * 0.6 + random.uniform(-2, 2)
        ctrl_y = y - blade_height * 0.6

        curves.QuadraticBezier(
            parent=self,
            start=(x, y),
            control=(ctrl_x, ctrl_y),
            end=(end_x, end_y),
            stroke=grass_color,
            stroke_width=random.uniform(0.4, 1.0),
            fill=None,
        )


if __name__ == "__main__":
    cli()
