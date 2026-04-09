"""
Outdoor Scene Example - Building drawings piece by piece with OD-DO

This example demonstrates how to compose complex drawings from multiple
sub-diagrams, each handling a specific element of the scene.

The scene includes:
- Background (sky and grassy ground with wavy horizon)
- Mountain with detailed strokes
- Flowing stream with ripples
- Hundreds of grass blades as small curved lines
- Sun with radiating rays
- A mythical faun from an external image
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from grass_text import GrassText
from od_do import cli, colors, diagram
from od_do.geometry import Point
from od_do.shapes import curves, image, polygon
from od_do.shapes.base import Rectangle
from wood_frame import WoodFrame

random.seed(42)


SCENE_WIDTH = 800
SCENE_HEIGHT = 600
HORIZON_Y = 350


def get_horizon_y(x):
    """Get the Y position of the horizon at a given X coordinate."""
    wave_amplitude = 8
    return HORIZON_Y + math.sin(x * 0.015) * wave_amplitude


class Sky(diagram.Diagram):
    """Blue sky background."""

    def draw(self):
        sky_color = colors.Color("#87CEEB")
        Rectangle(
            parent=self,
            ul=(0, 0),
            width=SCENE_WIDTH,
            height=SCENE_HEIGHT,
            fill=sky_color,
            stroke=None,
            stroke_width=0,
        )


class GrassGround(diagram.Diagram):
    """Green grass with wavy horizon - drawn over mountains."""

    def draw(self):
        grass_color = colors.Color("#4A7C23")

        path_d = f"M 0,{get_horizon_y(0)}"
        num_points = 100
        for i in range(1, num_points + 1):
            x = (i / num_points) * SCENE_WIDTH
            y = get_horizon_y(x)
            path_d += f" L {x},{y}"

        path_d += f" L {SCENE_WIDTH},{SCENE_HEIGHT} L 0,{SCENE_HEIGHT} Z"

        curves.BezierPath(
            parent=self,
            d=path_d,
            stroke=None,
            stroke_width=0,
            fill=grass_color,
        )


class Sun(diagram.Diagram):
    """A bright sun with radiating rays."""

    def draw(self):
        sun_x = 680
        sun_y = 120
        sun_radius = 40

        sun_color = colors.Color("#FFD93D")
        sun_glow = sun_color.lighten(0.3)

        polygon.RegularPolygon(
            parent=self,
            center=(sun_x, sun_y),
            radius=sun_radius + 10,
            sides=24,
            fill=sun_glow.alpha(0.4),
            stroke=None,
            stroke_width=0,
        )

        polygon.RegularPolygon(
            parent=self,
            center=(sun_x, sun_y),
            radius=sun_radius,
            sides=32,
            fill=sun_color,
            stroke=colors.Color("#F5A623"),
            stroke_width=2,
        )

        self._draw_rays(sun_x, sun_y, sun_radius)

    def _draw_rays(self, cx, cy, radius):
        num_rays = 16
        ray_length_short = 18
        ray_length_long = 30
        inner_gap = 10

        for i in range(num_rays):
            angle = (2 * math.pi * i) / num_rays
            is_long = i % 2 == 0
            ray_length = ray_length_long if is_long else ray_length_short

            start_x = cx + (radius + inner_gap) * math.cos(angle)
            start_y = cy + (radius + inner_gap) * math.sin(angle)
            end_x = cx + (radius + inner_gap + ray_length) * math.cos(angle)
            end_y = cy + (radius + inner_gap + ray_length) * math.sin(angle)

            ctrl_offset = random.uniform(-8, 8)
            ctrl_x = (start_x + end_x) / 2 + ctrl_offset * math.sin(angle)
            ctrl_y = (start_y + end_y) / 2 - ctrl_offset * math.cos(angle)

            ray_color = colors.Color("#FFE066") if is_long else colors.Color("#FFD93D")

            curves.QuadraticBezier(
                parent=self,
                start=(start_x, start_y),
                control=(ctrl_x, ctrl_y),
                end=(end_x, end_y),
                stroke=ray_color,
                stroke_width=3 if is_long else 2,
                fill=None,
            )


class MountainRange(diagram.Diagram):
    """Distant mountain range with snow-capped peaks - behind the grass."""

    def draw(self):
        base_y = HORIZON_Y + 25

        self._draw_mountain(
            320, 175, 180, 460, base_y, colors.Color("#9AABB8"), 0.7, 28
        )
        self._draw_mountain(
            560, 185, 440, 680, base_y, colors.Color("#8A9BAA"), 0.8, 24
        )
        self._draw_mountain(
            400, 145, 250, 550, base_y, colors.Color("#6B7B8C"), 1.0, 38
        )

    def _draw_mountain(
        self, peak_x, peak_y, left_x, right_x, base_y, color, opacity, snow_size
    ):
        """Draw a single mountain with snow cap and details."""
        path = f"M {left_x},{base_y} L {peak_x},{peak_y} L {right_x},{base_y} Z"
        curves.BezierPath(
            parent=self,
            d=path,
            stroke=color.darken(0.2).alpha(opacity * 0.5),
            stroke_width=1,
            fill=color.alpha(opacity),
        )

        if opacity == 1.0:
            shadow_path = (
                f"M {peak_x},{peak_y} L {right_x},{base_y} L {peak_x + 20},{base_y} Z"
            )
            curves.BezierPath(
                parent=self,
                d=shadow_path,
                stroke=None,
                stroke_width=0,
                fill=color.darken(0.3).alpha(0.4),
            )

        left_slope = (peak_x - left_x) / (base_y - peak_y)
        right_slope = (right_x - peak_x) / (base_y - peak_y)
        snow_left = peak_x - snow_size * left_slope
        snow_right = peak_x + snow_size * right_slope
        snow_bottom = peak_y + snow_size

        snow_mid1 = snow_left + (peak_x - snow_left) * 0.4
        snow_mid2 = peak_x + (snow_right - peak_x) * 0.5
        snow_path = (
            f"M {peak_x},{peak_y} "
            f"L {snow_left},{snow_bottom} "
            f"Q {snow_mid1},{snow_bottom + 6} {peak_x - 5},{snow_bottom + 3} "
            f"Q {snow_mid2},{snow_bottom + 8} {snow_right},{snow_bottom - 2} "
            f"L {peak_x},{peak_y}"
        )
        curves.BezierPath(
            parent=self,
            d=snow_path,
            stroke=None,
            stroke_width=0,
            fill=colors.WHITE.alpha(0.95 * opacity),
        )

        self._draw_details(
            peak_x, peak_y, left_x, right_x, base_y, snow_bottom, color, opacity
        )

    def _draw_details(
        self, peak_x, peak_y, left_x, right_x, base_y, snow_bottom, color, opacity
    ):
        """Add texture lines to mountain."""
        detail_color = color.darken(0.25)

        for _ in range(int(12 * opacity)):
            y = random.uniform(snow_bottom + 10, base_y - 40)
            t = (y - peak_y) / (base_y - peak_y)
            left_edge = peak_x - t * (peak_x - left_x)
            right_edge = peak_x + t * (right_x - peak_x)
            x = random.uniform(left_edge + 10, right_edge - 10)

            length = random.uniform(8, 18)
            angle = random.uniform(1.2, 1.9)

            curves.QuadraticBezier(
                parent=self,
                start=(x, y),
                control=(
                    x + length * 0.5 * math.cos(angle),
                    y + length * 0.5 * math.sin(angle),
                ),
                end=(x + length * math.cos(angle), y + length * math.sin(angle)),
                stroke=detail_color.alpha(0.3 * opacity),
                stroke_width=random.uniform(0.5, 1.0),
                fill=None,
            )

        snow_detail = colors.Color("#D0DCE5")
        for _ in range(int(4 * opacity)):
            sy = peak_y + random.uniform(10, snow_bottom - peak_y - 8)
            t = (sy - peak_y) / (snow_bottom - peak_y)
            max_x = 20 * t
            sx = peak_x + random.uniform(-max_x, max_x * 0.7)
            length = random.uniform(5, 10)
            angle = random.uniform(1.3, 1.7)

            curves.QuadraticBezier(
                parent=self,
                start=(sx, sy),
                control=(sx + length * 0.5, sy + length * 0.4),
                end=(sx + length * math.cos(angle), sy + length * math.sin(angle)),
                stroke=snow_detail.alpha(0.4 * opacity),
                stroke_width=random.uniform(0.4, 0.8),
                fill=None,
            )


STREAM_Y = HORIZON_Y + 70
STREAM_WIDTH = 28


def get_stream_y(x):
    """Get the Y position of the stream center at a given X coordinate."""
    return STREAM_Y + math.sin(x * 0.008) * 12 + math.sin(x * 0.02) * 5


class Stream(diagram.Diagram):
    """A flowing stream with water ripples."""

    def draw(self):
        stream_color = colors.Color("#5DADE2")
        stream_dark = colors.Color("#2E86AB")

        self._draw_stream_body(stream_color, stream_dark)
        self._draw_ripples()

    def _draw_stream_body(self, fill_color, stroke_color):
        num_points = 60

        upper_path = f"M 0,{get_stream_y(0) - STREAM_WIDTH/2}"
        for i in range(1, num_points + 1):
            x = (i / num_points) * SCENE_WIDTH
            y = get_stream_y(x) - STREAM_WIDTH / 2
            upper_path += f" L {x},{y}"

        lower_path = ""
        for i in range(num_points, -1, -1):
            x = (i / num_points) * SCENE_WIDTH
            y = get_stream_y(x) + STREAM_WIDTH / 2
            lower_path += f" L {x},{y}"

        full_path = upper_path + lower_path + " Z"

        curves.BezierPath(
            parent=self,
            d=full_path,
            stroke=stroke_color,
            stroke_width=2,
            fill=fill_color.alpha(0.75),
        )

    def _draw_ripples(self):
        ripple_color = colors.Color("#FFFFFF")
        num_ripples = 50

        for _ in range(num_ripples):
            x = random.uniform(20, SCENE_WIDTH - 20)
            y = get_stream_y(x) + random.uniform(
                -STREAM_WIDTH * 0.3, STREAM_WIDTH * 0.3
            )

            ripple_width = random.uniform(5, 12)
            curves.Arc(
                parent=self,
                center=(x, y),
                radius=ripple_width,
                start_angle=30,
                end_angle=150,
                stroke=ripple_color.alpha(random.uniform(0.25, 0.5)),
                stroke_width=random.uniform(0.5, 1.0),
                fill=None,
            )


def is_in_stream(x, y):
    """Check if a point is inside the stream area."""
    stream_center = get_stream_y(x)
    return abs(y - stream_center) < STREAM_WIDTH / 2 + 5


class GrassField(diagram.Diagram):
    """Hundreds of grass blades as small curved lines."""

    def draw(self):
        num_blades = 5400
        grass_area_top = HORIZON_Y + 12
        grass_area_bottom = SCENE_HEIGHT - 5

        for _ in range(num_blades):
            x = random.uniform(5, SCENE_WIDTH - 5)
            y = random.uniform(grass_area_top, grass_area_bottom)

            horizon_at_x = get_horizon_y(x)
            if y < horizon_at_x + 8:
                y = horizon_at_x + random.uniform(8, 25)

            if is_in_stream(x, y):
                continue

            self._draw_grass_blade(x, y)

    def _draw_grass_blade(self, x, y):
        green_base = random.randint(70, 130)
        green_var = random.randint(-25, 25)
        grass_color = colors.Color(
            (
                random.randint(25, 70),
                green_base + green_var,
                random.randint(15, 50),
            )
        )

        blade_height = random.uniform(8, 22)
        blade_curve = random.uniform(-10, 10)

        end_x = x + blade_curve
        end_y = y - blade_height

        ctrl_x = x + blade_curve * 0.6 + random.uniform(-3, 3)
        ctrl_y = y - blade_height * 0.6

        curves.QuadraticBezier(
            parent=self,
            start=(x, y),
            control=(ctrl_x, ctrl_y),
            end=(end_x, end_y),
            stroke=grass_color,
            stroke_width=random.uniform(0.6, 1.5),
            fill=None,
        )


class TreeSilhouette(diagram.Diagram):
    """Simple tree silhouettes for depth."""

    def draw(self):
        tree_positions = [
            (80, get_horizon_y(80) + 5, 0.8),
            (180, get_horizon_y(180) + 15, 0.6),
            (720, get_horizon_y(720) + 10, 0.7),
        ]

        for tx, ty, scale in tree_positions:
            self._draw_tree(tx, ty, scale)

    def _draw_tree(self, x, y, scale):
        trunk_height = 30 * scale
        trunk_width = 8 * scale
        canopy_radius = 35 * scale

        tree_color = colors.Color("#2D5016")

        Rectangle(
            parent=self,
            ul=(x - trunk_width / 2, y - trunk_height),
            width=trunk_width,
            height=trunk_height,
            fill=colors.Color("#4A3728"),
            stroke=None,
            stroke_width=0,
        )

        num_circles = 5
        for i in range(num_circles):
            offset_x = random.uniform(-canopy_radius * 0.4, canopy_radius * 0.4)
            offset_y = random.uniform(-canopy_radius * 0.3, canopy_radius * 0.3)
            r = canopy_radius * random.uniform(0.5, 0.9)

            polygon.RegularPolygon(
                parent=self,
                center=(
                    x + offset_x,
                    y - trunk_height - canopy_radius * 0.5 + offset_y,
                ),
                radius=r,
                sides=12,
                fill=tree_color.alpha(0.8),
                stroke=tree_color.darken(0.2),
                stroke_width=1,
            )


class Clouds(diagram.Diagram):
    """Fluffy clouds in the sky."""

    def draw(self):
        cloud_positions = [
            (120, 80, 1.0),
            (300, 120, 0.7),
            (480, 70, 0.85),
        ]

        for cx, cy, scale in cloud_positions:
            self._draw_cloud(cx, cy, scale)

    def _draw_cloud(self, x, y, scale):
        cloud_color = colors.WHITE.alpha(0.9)
        num_puffs = random.randint(4, 7)

        for i in range(num_puffs):
            offset_x = (i - num_puffs / 2) * 25 * scale + random.uniform(-10, 10)
            offset_y = random.uniform(-15, 15) * scale
            radius = random.uniform(20, 35) * scale

            polygon.RegularPolygon(
                parent=self,
                center=(x + offset_x, y + offset_y),
                radius=radius,
                sides=16,
                fill=cloud_color,
                stroke=None,
                stroke_width=0,
            )


class FaunCharacter(diagram.Diagram):
    """The faun character from an external PNG."""

    def draw(self):
        faun_path = Path(__file__).parent / "monster-faun-greek-flat-by-Vexels.png"

        image.Image(
            parent=self,
            file_path=str(faun_path),
            width=180,
            height=180,
            ll=(480, SCENE_HEIGHT - 30),
        )


class OutdoorScene(diagram.Diagram):
    """Main scene composing all elements."""

    render_padding = 0

    def draw(self):
        Sky(parent=self)
        MountainRange(parent=self, rotation=2, ll=(220, 350))
        Clouds(parent=self)
        Sun(parent=self, rotation=10, ll=(630, 100))
        GrassGround(parent=self)
        TreeSilhouette(parent=self)
        Stream(parent=self)
        GrassField(parent=self)
        FaunCharacter(parent=self, ll=(550, 550))
        GrassText(parent=self, ll=(45, SCENE_HEIGHT - 45))
        WoodFrame(parent=self)


if __name__ == "__main__":
    cli()
