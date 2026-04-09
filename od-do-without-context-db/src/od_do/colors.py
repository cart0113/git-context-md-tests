"""
Color module for OD-DO diagrams.

Provides a Color class with manipulation methods (lighten, darken, blend, alpha)
and a comprehensive set of predefined color constants.

Example:
    from od_do import colors

    # Use predefined colors
    fill = colors.RED
    stroke = colors.DARK_BLUE

    # Create custom colors
    custom = colors.Color("#8B4789")

    # Manipulate colors
    lighter = colors.RED.lighten(0.3)
    darker = colors.BLUE.darken(0.2)
    transparent = colors.GREEN.alpha(0.5)
    mixed = colors.RED.blend(colors.BLUE, 0.5)
"""

from __future__ import annotations

from typing import Tuple, Union

ColorLike = Union["Color", str, Tuple[str, float]]


class Color:
    """A color with manipulation methods for diagram styling.

    Colors are stored internally as RGBA values (0-255 for RGB, 0.0-1.0 for alpha).
    Can be created from hex strings (#RGB, #RRGGBB, #RRGGBBAA) or RGB/RGBA tuples.

    Attributes:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        a: Alpha component (0.0-1.0, where 1.0 is fully opaque)

    Example:
        red = Color("#FF0000")
        blue = Color("#0000FF")
        purple = red.blend(blue, 0.5)
        transparent_red = red.alpha(0.5)
    """

    def __init__(
        self,
        value: Union[str, Tuple[int, int, int], Tuple[int, int, int, float]],
    ):
        """Create a Color from a hex string or RGB/RGBA tuple.

        Args:
            value: Color specification. Can be:
                - Hex string: "#RGB", "#RRGGBB", or "#RRGGBBAA"
                - RGB tuple: (r, g, b) with values 0-255
                - RGBA tuple: (r, g, b, a) with RGB 0-255 and alpha 0.0-1.0
        """
        if isinstance(value, str):
            self.r, self.g, self.b, self.a = self._parse_hex(value)
        elif isinstance(value, tuple):
            if len(value) == 3:
                self.r, self.g, self.b = value
                self.a = 1.0
            elif len(value) == 4:
                self.r, self.g, self.b = value[0], value[1], value[2]
                self.a = value[3]
            else:
                raise ValueError(f"Invalid tuple length: {len(value)}")
        else:
            raise TypeError(f"Cannot create Color from {type(value)}")

    def _parse_hex(self, hex_str: str) -> Tuple[int, int, int, float]:
        """Parse a hex color string into RGBA components."""
        hex_str = hex_str.lstrip("#")

        if len(hex_str) == 3:
            # #RGB -> #RRGGBB
            r = int(hex_str[0] * 2, 16)
            g = int(hex_str[1] * 2, 16)
            b = int(hex_str[2] * 2, 16)
            a = 1.0
        elif len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = 1.0
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16) / 255.0
        else:
            raise ValueError(f"Invalid hex color: #{hex_str}")

        return r, g, b, a

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Return RGB tuple (0-255 for each component)."""
        return (self.r, self.g, self.b)

    @property
    def rgba(self) -> Tuple[int, int, int, float]:
        """Return RGBA tuple (0-255 for RGB, 0.0-1.0 for alpha)."""
        return (self.r, self.g, self.b, self.a)

    @property
    def hex(self) -> str:
        """Return hex string (#RRGGBB or #RRGGBBAA if alpha < 1)."""
        if self.a >= 1.0:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        else:
            alpha_hex = int(self.a * 255)
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{alpha_hex:02x}"

    @property
    def hex_rgb(self) -> str:
        """Return hex string (#RRGGBB), ignoring alpha."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def alpha(self, a: float) -> Color:
        """Return a new Color with the specified alpha value.

        Args:
            a: Alpha value (0.0 = fully transparent, 1.0 = fully opaque)

        Returns:
            New Color with the same RGB but different alpha.

        Example:
            transparent_red = colors.RED.alpha(0.5)
        """
        return Color((self.r, self.g, self.b, a))

    def lighten(self, amount: float) -> Color:
        """Return a lighter version of this color.

        Args:
            amount: How much to lighten (0.0 = no change, 1.0 = white)

        Returns:
            New Color that is lighter.

        Example:
            light_blue = colors.BLUE.lighten(0.3)
        """
        r = min(255, int(self.r + (255 - self.r) * amount))
        g = min(255, int(self.g + (255 - self.g) * amount))
        b = min(255, int(self.b + (255 - self.b) * amount))
        return Color((r, g, b, self.a))

    def darken(self, amount: float) -> Color:
        """Return a darker version of this color.

        Args:
            amount: How much to darken (0.0 = no change, 1.0 = black)

        Returns:
            New Color that is darker.

        Example:
            dark_red = colors.RED.darken(0.3)
        """
        r = max(0, int(self.r * (1 - amount)))
        g = max(0, int(self.g * (1 - amount)))
        b = max(0, int(self.b * (1 - amount)))
        return Color((r, g, b, self.a))

    def blend(self, other: Color, weight: float = 0.5) -> Color:
        """Blend this color with another color.

        Args:
            other: The color to blend with.
            weight: Blend weight (0.0 = this color, 1.0 = other color)

        Returns:
            New Color that is a blend of both colors.

        Example:
            purple = colors.RED.blend(colors.BLUE, 0.5)
        """
        r = int(self.r * (1 - weight) + other.r * weight)
        g = int(self.g * (1 - weight) + other.g * weight)
        b = int(self.b * (1 - weight) + other.b * weight)
        a = self.a * (1 - weight) + other.a * weight
        return Color((r, g, b, a))

    def saturate(self, amount: float) -> Color:
        """Increase the saturation of this color.

        Args:
            amount: How much to saturate (0.0 = no change, 1.0 = full saturation)

        Returns:
            New Color with increased saturation.
        """
        gray = int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)
        r = min(255, max(0, int(gray + (self.r - gray) * (1 + amount))))
        g = min(255, max(0, int(gray + (self.g - gray) * (1 + amount))))
        b = min(255, max(0, int(gray + (self.b - gray) * (1 + amount))))
        return Color((r, g, b, self.a))

    def desaturate(self, amount: float) -> Color:
        """Decrease the saturation of this color.

        Args:
            amount: How much to desaturate (0.0 = no change, 1.0 = grayscale)

        Returns:
            New Color with decreased saturation.
        """
        gray = int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)
        r = int(self.r + (gray - self.r) * amount)
        g = int(self.g + (gray - self.g) * amount)
        b = int(self.b + (gray - self.b) * amount)
        return Color((r, g, b, self.a))

    def invert(self) -> Color:
        """Return the inverted (complementary) color.

        Returns:
            New Color with inverted RGB values.
        """
        return Color((255 - self.r, 255 - self.g, 255 - self.b, self.a))

    def grayscale(self) -> Color:
        """Return a grayscale version of this color.

        Returns:
            New Color in grayscale.
        """
        gray = int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)
        return Color((gray, gray, gray, self.a))

    def css_rgba(self) -> str:
        """Return CSS rgba() string representation."""
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"

    def svg_color(self) -> str:
        """Return color string suitable for SVG fill/stroke attributes.

        Returns hex for opaque colors, rgba() for transparent.
        """
        if self.a >= 1.0:
            return self.hex_rgb
        else:
            return self.css_rgba()

    def __str__(self) -> str:
        """Return hex representation."""
        return self.hex

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Color({self.hex!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Color."""
        if not isinstance(other, Color):
            return NotImplemented
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __hash__(self) -> int:
        """Return hash for use in sets/dicts."""
        return hash((self.r, self.g, self.b, self.a))

    @classmethod
    def resolve_color(cls, color: ColorLike) -> Color:
        """Resolve a Color, hex string, or (hex, alpha) tuple to a Color object.

        Args:
            color: A Color object, hex string, or tuple of (hex_string, alpha).
                   When a tuple is provided, the second element must be a float
                   between 0.0 and 1.0 representing the alpha value.

        Returns:
            The same Color if already a Color, otherwise a new Color from the
            string or tuple.

        Example:
            Color.resolve_color("#ff6b6b")           # Color from hex
            Color.resolve_color(("#ff6b6b", 0.5))    # Color with 50% alpha
            Color.resolve_color(colors.RED)          # Returns the same Color
        """
        if isinstance(color, cls):
            return color
        if isinstance(color, str):
            return cls(color)
        return cls(color[0]).alpha(color[1])


# =============================================================================
# Color Constants
# =============================================================================

# Basic Colors
WHITE = Color("#FFFFFF")
BLACK = Color("#000000")
RED = Color("#FF0000")
GREEN = Color("#00FF00")
BLUE = Color("#0000FF")
YELLOW = Color("#FFFF00")
CYAN = Color("#00FFFF")
MAGENTA = Color("#FF00FF")

# Grays
LIGHT_GRAY = Color("#D3D3D3")
GRAY = Color("#808080")
DARK_GRAY = Color("#404040")
CHARCOAL = Color("#36454F")
SLATE = Color("#708090")

# Reds
LIGHT_RED = Color("#FF6B6B")
DARK_RED = Color("#8B0000")
CRIMSON = Color("#DC143C")
CORAL = Color("#FF7F50")
SALMON = Color("#FA8072")
TOMATO = Color("#FF6347")
INDIAN_RED = Color("#CD5C5C")
MAROON = Color("#800000")
FIRE_BRICK = Color("#B22222")

# Oranges
ORANGE = Color("#FFA500")
DARK_ORANGE = Color("#FF8C00")
LIGHT_ORANGE = Color("#FFD39B")
BURNT_ORANGE = Color("#CC5500")
PEACH = Color("#FFCBA4")
TANGERINE = Color("#FF9966")
AMBER = Color("#FFBF00")

# Yellows
LIGHT_YELLOW = Color("#FFFFE0")
GOLD = Color("#FFD700")
MUSTARD = Color("#FFDB58")
LEMON = Color("#FFF44F")
KHAKI = Color("#F0E68C")

# Greens
LIGHT_GREEN = Color("#90EE90")
DARK_GREEN = Color("#006400")
LIME = Color("#32CD32")
FOREST = Color("#228B22")
OLIVE = Color("#808000")
SEA_GREEN = Color("#2E8B57")
SPRING_GREEN = Color("#00FF7F")
EMERALD = Color("#50C878")
JADE = Color("#00A86B")
MINT = Color("#98FF98")
SAGE = Color("#9DC183")
TEAL = Color("#008080")

# Blues
LIGHT_BLUE = Color("#ADD8E6")
DARK_BLUE = Color("#00008B")
SKY_BLUE = Color("#87CEEB")
STEEL_BLUE = Color("#4682B4")
NAVY = Color("#000080")
ROYAL_BLUE = Color("#4169E1")
DODGER_BLUE = Color("#1E90FF")
POWDER_BLUE = Color("#B0E0E6")
CORNFLOWER = Color("#6495ED")
SAPPHIRE = Color("#0F52BA")
COBALT = Color("#0047AB")
AZURE = Color("#007FFF")

# Purples
PURPLE = Color("#800080")
LIGHT_PURPLE = Color("#DDA0DD")
DARK_PURPLE = Color("#301934")
VIOLET = Color("#EE82EE")
INDIGO = Color("#4B0082")
LAVENDER = Color("#E6E6FA")
ORCHID = Color("#DA70D6")
PLUM = Color("#DDA0DD")
AMETHYST = Color("#9966CC")
MAUVE = Color("#E0B0FF")
GRAPE = Color("#6F2DA8")

# Pinks
PINK = Color("#FFC0CB")
LIGHT_PINK = Color("#FFB6C1")
HOT_PINK = Color("#FF69B4")
DEEP_PINK = Color("#FF1493")
ROSE = Color("#FF007F")
BLUSH = Color("#DE5D83")
FUCHSIA = Color("#FF00FF")

# Browns
BROWN = Color("#A52A2A")
LIGHT_BROWN = Color("#C4A484")
DARK_BROWN = Color("#654321")
SIENNA = Color("#A0522D")
CHOCOLATE = Color("#D2691E")
TAN = Color("#D2B48C")
BEIGE = Color("#F5F5DC")
WHEAT = Color("#F5DEB3")
COFFEE = Color("#6F4E37")
SEPIA = Color("#704214")
UMBER = Color("#635147")

# Metals
SILVER = Color("#C0C0C0")
BRONZE = Color("#CD7F32")
COPPER = Color("#B87333")
BRASS = Color("#B5A642")

# Material Design inspired colors
MD_RED = Color("#F44336")
MD_PINK = Color("#E91E63")
MD_PURPLE = Color("#9C27B0")
MD_DEEP_PURPLE = Color("#673AB7")
MD_INDIGO = Color("#3F51B5")
MD_BLUE = Color("#2196F3")
MD_LIGHT_BLUE = Color("#03A9F4")
MD_CYAN = Color("#00BCD4")
MD_TEAL = Color("#009688")
MD_GREEN = Color("#4CAF50")
MD_LIGHT_GREEN = Color("#8BC34A")
MD_LIME = Color("#CDDC39")
MD_YELLOW = Color("#FFEB3B")
MD_AMBER = Color("#FFC107")
MD_ORANGE = Color("#FF9800")
MD_DEEP_ORANGE = Color("#FF5722")
MD_BROWN = Color("#795548")
MD_GRAY = Color("#9E9E9E")
MD_BLUE_GRAY = Color("#607D8B")

# Transparent
TRANSPARENT = Color((0, 0, 0, 0.0))

# Common UI colors
SUCCESS = Color("#28A745")
WARNING = Color("#FFC107")
DANGER = Color("#DC3545")
INFO = Color("#17A2B8")
PRIMARY = Color("#007BFF")
SECONDARY = Color("#6C757D")
