# Text and Tables

OD-DO provides rich text rendering capabilities with alignment options and table
widgets for structured data display.

## Text Shapes

### Text

Basic text element with positioning and alignment control.

```python
from od_do.shapes import text
from od_do import colors

# Simple text
text.Text(
    parent=diagram,
    position=(100, 100),
    content="Hello World",
    font_size=14,
    color=colors.BLACK,
)

# Centered text
text.Text(
    parent=diagram,
    position=(200, 100),
    content="Centered",
    font_size=16,
    color=colors.DARK_BLUE,
    align="center",
    valign="middle",
)

# Multiline text
text.Text(
    parent=diagram,
    position=(100, 150),
    content="Line 1\nLine 2\nLine 3",
    font_size=12,
    color=colors.BLACK,
)
```

**Parameters:**

| Parameter     | Type        | Default          | Description                               |
| ------------- | ----------- | ---------------- | ----------------------------------------- |
| `parent`      | Diagram     | required         | Parent diagram                            |
| `position`    | tuple/Point | required         | Anchor position (x, y)                    |
| `content`     | str         | required         | Text content (supports `\n` for newlines) |
| `font_size`   | float       | 14               | Font size in pixels                       |
| `font_family` | str         | "sans-serif"     | Font family                               |
| `font_weight` | str         | "normal"         | Font weight ("normal", "bold")            |
| `color`       | ColorLike   | BLACK            | Text color                                |
| `align`       | str         | "left"           | Horizontal: "left", "center", "right"     |
| `valign`      | str         | "top"            | Vertical: "top", "middle", "bottom"       |
| `line_height` | float       | font_size \* 1.2 | Line spacing                              |

### TextBox

A rectangular box with text inside. Text is automatically aligned within the
box.

```python
# Centered text in a box
text.TextBox(
    parent=diagram,
    ll=(100, 200),
    width=150,
    height=50,
    content="Centered Text",
    align="center",
    valign="middle",
    fill=colors.LIGHT_BLUE,
    stroke=colors.DARK_BLUE,
)

# With rounded corners
text.TextBox(
    parent=diagram,
    ll=(100, 280),
    width=150,
    height=50,
    content="Rounded Box",
    corners="round",
    fill=colors.LIGHT_GREEN,
    stroke=colors.DARK_GREEN,
)
```

**Parameters:**

| Parameter      | Type        | Default      | Description                |
| -------------- | ----------- | ------------ | -------------------------- |
| `parent`       | Diagram     | required     | Parent diagram             |
| `ll`           | tuple/Point | required     | Lower-left corner position |
| `width`        | float       | required     | Box width                  |
| `height`       | float       | required     | Box height                 |
| `content`      | str         | required     | Text content               |
| `font_size`    | float       | 14           | Font size                  |
| `font_family`  | str         | "sans-serif" | Font family                |
| `font_weight`  | str         | "normal"     | Font weight                |
| `text_color`   | ColorLike   | BLACK        | Text color                 |
| `align`        | str         | "center"     | Horizontal alignment       |
| `valign`       | str         | "middle"     | Vertical alignment         |
| `padding`      | float       | 5            | Padding inside box         |
| `fill`         | ColorLike   | None         | Box fill color             |
| `stroke`       | ColorLike   | None         | Box stroke color           |
| `stroke_width` | float       | 1            | Stroke width               |
| `corners`      | str         | None         | Corner style (see below)   |

### Label

Auto-sizing text label with optional background. Unlike TextBox, Label
automatically sizes to fit content.

```python
# Simple label
text.Label(
    parent=diagram,
    position=(100, 100),
    content="Status: Active",
    padding=6,
    fill=colors.LIGHT_GREEN,
    stroke=colors.DARK_GREEN,
)

# Rounded label
text.Label(
    parent=diagram,
    position=(200, 100),
    content="Warning",
    padding=8,
    fill=colors.LIGHT_YELLOW,
    stroke=colors.GOLD,
    corners="very-round",
)
```

**Parameters:**

| Parameter      | Type        | Default      | Description          |
| -------------- | ----------- | ------------ | -------------------- |
| `parent`       | Diagram     | required     | Parent diagram       |
| `position`     | tuple/Point | required     | Anchor position      |
| `content`      | str         | required     | Text content         |
| `font_size`    | float       | 12           | Font size            |
| `font_family`  | str         | "sans-serif" | Font family          |
| `font_weight`  | str         | "normal"     | Font weight          |
| `text_color`   | ColorLike   | BLACK        | Text color           |
| `align`        | str         | "left"       | Horizontal alignment |
| `valign`       | str         | "top"        | Vertical alignment   |
| `padding`      | float       | 4            | Padding around text  |
| `fill`         | ColorLike   | None         | Background fill      |
| `stroke`       | ColorLike   | None         | Border stroke        |
| `stroke_width` | float       | 1            | Stroke width         |
| `corners`      | str         | None         | Corner style         |

## Alignment Options

### Horizontal Alignment (`align`)

- `"left"` - Text anchored at left edge (default for Text/Label)
- `"center"` - Text centered horizontally (default for TextBox)
- `"right"` - Text anchored at right edge

### Vertical Alignment (`valign`)

- `"top"` - Text anchored at top (default for Text/Label)
- `"middle"` - Text centered vertically (default for TextBox)
- `"bottom"` - Text anchored at bottom

### Corner Styles (`corners`)

- `None` - Sharp corners (default)
- `"slightly-round"` - 5% of minimum dimension
- `"round"` - 10% of minimum dimension
- `"very-round"` - 20% of minimum dimension
- `"round:0.15"` - Custom factor (15% in this example)

## Using Block as TextBox

The basic `Block` shape can serve as a text background. Place text on top with
manual positioning:

```python
from od_do import colors
from od_do.shapes import text, Block

# Block as background
Block(
    parent=diagram,
    ll=(100, 200),
    width=150,
    height=50,
    fill=colors.LIGHT_GRAY,
    stroke=colors.DARK_GRAY,
    stroke_width=1,
)

# Text overlay (positioned at center of block)
text.Text(
    parent=diagram,
    position=(175, 175),  # center of block
    content="Block + Text",
    align="center",
    valign="middle",
)
```

For integrated text+box, use `TextBox` instead - it handles alignment
automatically.

## Table Shapes

### Table

General-purpose table with header row and data rows.

```python
from od_do.shapes import table
from od_do import colors

table.Table(
    parent=diagram,
    ll=(100, 300),
    columns=["Name", "Type", "Description"],
    rows=[
        ["id", "int", "Primary key"],
        ["name", "string", "User name"],
        ["email", "string", "Email address"],
    ],
    header_fill=colors.DARK_BLUE,
    header_text_color=colors.WHITE,
    fill=colors.WHITE,
    stroke=colors.BLACK,
)
```

**Parameters:**

| Parameter           | Type            | Default      | Description          |
| ------------------- | --------------- | ------------ | -------------------- |
| `parent`            | Diagram         | required     | Parent diagram       |
| `ll`                | tuple/Point     | required     | Lower-left position  |
| `columns`           | List[str]       | required     | Column headers       |
| `rows`              | List[List[str]] | required     | Data rows            |
| `column_widths`     | List[float]     | auto         | Column widths        |
| `row_height`        | float           | 25           | Row height           |
| `header_height`     | float           | row_height   | Header row height    |
| `font_size`         | float           | 12           | Font size            |
| `font_family`       | str             | "sans-serif" | Font family          |
| `padding`           | float           | 8            | Cell padding         |
| `fill`              | ColorLike       | None         | Row fill color       |
| `stroke`            | ColorLike       | BLACK        | Border color         |
| `stroke_width`      | float           | 1            | Border width         |
| `header_fill`       | ColorLike       | None         | Header fill          |
| `header_text_color` | ColorLike       | BLACK        | Header text color    |
| `text_color`        | ColorLike       | BLACK        | Cell text color      |
| `alternate_fill`    | ColorLike       | None         | Alternating row fill |

### EntityTable

Specialized table for ER (Entity-Relationship) diagrams with title, attributes,
and key indicators.

```python
table.EntityTable(
    parent=diagram,
    ll=(100, 400),
    title="users",
    rows=[
        ("id", "INT", "PK"),          # Primary Key
        ("username", "VARCHAR(50)", "UK"),   # Unique Key
        ("email", "VARCHAR(255)", ""),
        ("created_at", "TIMESTAMP", ""),
    ],
    title_fill=colors.DARK_BLUE,
    title_text_color=colors.WHITE,
    fill=colors.WHITE,
    stroke=colors.DARK_BLUE,
)
```

**Parameters:**

| Parameter          | Type        | Default      | Description              |
| ------------------ | ----------- | ------------ | ------------------------ |
| `parent`           | Diagram     | required     | Parent diagram           |
| `ll`               | tuple/Point | required     | Lower-left position      |
| `title`            | str         | required     | Entity/table name        |
| `rows`             | List[Tuple] | required     | (name, type, key) tuples |
| `column_widths`    | List[float] | auto         | Column widths            |
| `row_height`       | float       | 22           | Row height               |
| `title_height`     | float       | row_height+4 | Title row height         |
| `font_size`        | float       | 11           | Font size                |
| `font_family`      | str         | "monospace"  | Font family              |
| `padding`          | float       | 6            | Cell padding             |
| `fill`             | ColorLike   | WHITE        | Row fill                 |
| `stroke`           | ColorLike   | BLACK        | Border color             |
| `title_fill`       | ColorLike   | #4A90D9      | Title fill               |
| `title_text_color` | ColorLike   | WHITE        | Title text               |
| `text_color`       | ColorLike   | BLACK        | Cell text                |

**Key Indicators:**

- `"PK"` - Primary Key
- `"FK"` - Foreign Key
- `"UK"` - Unique Key
- `""` - No key constraint

### KeyValueTable

Simple two-column table for property/configuration display.

```python
table.KeyValueTable(
    parent=diagram,
    ll=(100, 500),
    items=[
        ("Host", "localhost"),
        ("Port", "5432"),
        ("Database", "myapp"),
        ("SSL", "enabled"),
    ],
    key_fill=colors.LIGHT_GRAY,
    fill=colors.WHITE,
    stroke=colors.DARK_GRAY,
)
```

**Parameters:**

| Parameter          | Type        | Default      | Description         |
| ------------------ | ----------- | ------------ | ------------------- |
| `parent`           | Diagram     | required     | Parent diagram      |
| `ll`               | tuple/Point | required     | Lower-left position |
| `items`            | List[Tuple] | required     | (key, value) pairs  |
| `key_width`        | float       | auto         | Key column width    |
| `value_width`      | float       | auto         | Value column width  |
| `row_height`       | float       | 22           | Row height          |
| `font_size`        | float       | 12           | Font size           |
| `font_family`      | str         | "sans-serif" | Font family         |
| `padding`          | float       | 6            | Cell padding        |
| `fill`             | ColorLike   | None         | Value column fill   |
| `stroke`           | ColorLike   | BLACK        | Border color        |
| `key_fill`         | ColorLike   | None         | Key column fill     |
| `key_text_color`   | ColorLike   | BLACK        | Key text color      |
| `value_text_color` | ColorLike   | BLACK        | Value text color    |

## Examples

See `examples/extended-shapes/text_example.py` and
`examples/extended-shapes/table_example.py` for complete working examples.

Run examples:

```bash
cd examples/extended-shapes
python text_example.py --output text_example.svg
python table_example.py --output table_example.svg
```
