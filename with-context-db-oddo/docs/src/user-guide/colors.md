# Colors

OD-DO provides a comprehensive color system with manipulation methods and
predefined constants.

## Basic Usage

```python
from od_do import colors

# Use predefined colors
fill = colors.RED
stroke = colors.DARK_BLUE

# Create custom colors from hex
custom = colors.Color("#8B4789")

# Create from RGB tuple
rgb_color = colors.Color((255, 128, 64))

# Create with alpha
transparent = colors.Color((255, 0, 0, 0.5))
```

## Color Manipulation

### Lightening and Darkening

```python
lighter = colors.RED.lighten(0.3)   # 30% lighter (0.0 = no change, 1.0 = white)
darker = colors.BLUE.darken(0.2)    # 20% darker (0.0 = no change, 1.0 = black)
```

### Alpha (Transparency)

```python
semi_transparent = colors.RED.alpha(0.5)   # 50% transparent
nearly_invisible = colors.BLUE.alpha(0.1)  # 90% transparent
```

### Blending

```python
purple = colors.RED.blend(colors.BLUE, 0.5)  # 50/50 mix
mostly_red = colors.RED.blend(colors.BLUE, 0.2)  # 80% red, 20% blue
```

### Saturation

```python
more_vivid = color.saturate(0.3)     # Increase saturation
muted = color.desaturate(0.5)        # Decrease saturation
grayscale = color.grayscale()        # Full desaturation
```

### Inversion

```python
inverted = colors.RED.invert()  # Returns cyan
```

## Color Properties

```python
color = colors.Color("#FF6B6B")

# Get color components
print(color.r, color.g, color.b)  # 255, 107, 107
print(color.a)                     # 1.0 (alpha)

# Get as tuple
print(color.rgb)                   # (255, 107, 107)
print(color.rgba)                  # (255, 107, 107, 1.0)

# Get as hex string
print(color.hex)                   # "#ff6b6b"
print(color.hex_rgb)               # "#ff6b6b" (ignores alpha)

# CSS representation
print(color.css_rgba())            # "rgba(255, 107, 107, 1.0)"
```

## Predefined Colors

### Basic Colors

| Name      | Value   | Preview |
| --------- | ------- | ------- |
| `WHITE`   | #FFFFFF | White   |
| `BLACK`   | #000000 | Black   |
| `RED`     | #FF0000 | Red     |
| `GREEN`   | #00FF00 | Green   |
| `BLUE`    | #0000FF | Blue    |
| `YELLOW`  | #FFFF00 | Yellow  |
| `CYAN`    | #00FFFF | Cyan    |
| `MAGENTA` | #FF00FF | Magenta |

### Grays

| Name         | Value   |
| ------------ | ------- |
| `LIGHT_GRAY` | #D3D3D3 |
| `GRAY`       | #808080 |
| `DARK_GRAY`  | #404040 |
| `CHARCOAL`   | #36454F |
| `SLATE`      | #708090 |

### Reds

| Name        | Value   |
| ----------- | ------- |
| `LIGHT_RED` | #FF6B6B |
| `DARK_RED`  | #8B0000 |
| `CRIMSON`   | #DC143C |
| `CORAL`     | #FF7F50 |
| `SALMON`    | #FA8072 |
| `TOMATO`    | #FF6347 |
| `MAROON`    | #800000 |

### Blues

| Name          | Value   |
| ------------- | ------- |
| `LIGHT_BLUE`  | #ADD8E6 |
| `DARK_BLUE`   | #00008B |
| `SKY_BLUE`    | #87CEEB |
| `NAVY`        | #000080 |
| `ROYAL_BLUE`  | #4169E1 |
| `DODGER_BLUE` | #1E90FF |
| `COBALT`      | #0047AB |

### Greens

| Name          | Value   |
| ------------- | ------- |
| `LIGHT_GREEN` | #90EE90 |
| `DARK_GREEN`  | #006400 |
| `LIME`        | #32CD32 |
| `FOREST`      | #228B22 |
| `EMERALD`     | #50C878 |
| `JADE`        | #00A86B |
| `MINT`        | #98FF98 |
| `TEAL`        | #008080 |

### Purples

| Name           | Value   |
| -------------- | ------- |
| `PURPLE`       | #800080 |
| `LIGHT_PURPLE` | #DDA0DD |
| `DARK_PURPLE`  | #301934 |
| `VIOLET`       | #EE82EE |
| `INDIGO`       | #4B0082 |
| `LAVENDER`     | #E6E6FA |
| `AMETHYST`     | #9966CC |

### Oranges and Yellows

| Name          | Value   |
| ------------- | ------- |
| `ORANGE`      | #FFA500 |
| `DARK_ORANGE` | #FF8C00 |
| `GOLD`        | #FFD700 |
| `MUSTARD`     | #FFDB58 |
| `AMBER`       | #FFBF00 |

### Pinks

| Name        | Value   |
| ----------- | ------- |
| `PINK`      | #FFC0CB |
| `HOT_PINK`  | #FF69B4 |
| `DEEP_PINK` | #FF1493 |
| `ROSE`      | #FF007F |

### Browns

| Name          | Value   |
| ------------- | ------- |
| `BROWN`       | #A52A2A |
| `LIGHT_BROWN` | #C4A484 |
| `DARK_BROWN`  | #654321 |
| `CHOCOLATE`   | #D2691E |
| `TAN`         | #D2B48C |
| `COFFEE`      | #6F4E37 |

### Material Design Colors

| Name        | Value   |
| ----------- | ------- |
| `MD_RED`    | #F44336 |
| `MD_PINK`   | #E91E63 |
| `MD_PURPLE` | #9C27B0 |
| `MD_INDIGO` | #3F51B5 |
| `MD_BLUE`   | #2196F3 |
| `MD_CYAN`   | #00BCD4 |
| `MD_TEAL`   | #009688 |
| `MD_GREEN`  | #4CAF50 |
| `MD_ORANGE` | #FF9800 |

### UI Colors

| Name        | Usage                    |
| ----------- | ------------------------ |
| `SUCCESS`   | Green for success states |
| `WARNING`   | Yellow for warnings      |
| `DANGER`    | Red for errors           |
| `INFO`      | Blue for information     |
| `PRIMARY`   | Primary action color     |
| `SECONDARY` | Secondary action color   |

### Special

| Name          | Description       |
| ------------- | ----------------- |
| `TRANSPARENT` | Fully transparent |

## Using Colors with Shapes

```python
from od_do import diagram, colors
from od_do.shapes import Block, Circle

class ColorfulDiagram(diagram.Diagram):
    def draw(self):
        # Solid color
        Block(
            parent=self,
            ll=(50, 100),
            width=100,
            height=50,
            fill=colors.RED,
            stroke=colors.BLACK,
            stroke_width=1,
        )

        # Transparent fill
        Block(
            parent=self,
            ll=(200, 100),
            width=100,
            height=50,
            fill=colors.BLUE.alpha(0.5),
            stroke=colors.DARK_BLUE,
            stroke_width=1,
        )

        # Lightened color
        Circle(
            parent=self,
            center=(400, 125),
            radius=40,
            fill=colors.GREEN.lighten(0.3),
            stroke=colors.DARK_GREEN,
            stroke_width=1,
        )

        # Blended color
        Block(
            parent=self,
            ll=(500, 100),
            width=100,
            height=50,
            fill=colors.RED.blend(colors.YELLOW, 0.5),  # Orange
            stroke=colors.ORANGE.darken(0.3),
            stroke_width=1,
        )
```
