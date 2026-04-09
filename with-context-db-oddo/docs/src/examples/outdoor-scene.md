# Outdoor Scene

![Outdoor Scene](OutdoorScene.svg ':size=100%')

This example demonstrates building complex drawings piece by piece using od-do
primitives. It showcases layered composition, atmospheric perspective, and
extensive use of curves and random variation.

## Scene Composition

The scene is composed of multiple diagram classes, drawn in a specific order to
achieve proper layering:

1. **Sky** - Blue background rectangle
2. **MountainRange** - Three mountains with snow caps (drawn BEFORE grass so
   they appear behind)
3. **Clouds** - Fluffy cloud shapes
4. **Sun** - Sun with radiating curved rays
5. **GrassGround** - Green grass fill with wavy horizon (covers mountain bases)
6. **TreeSilhouette** - Simple trees at the horizon
7. **Stream** - Curved flowing water with ripples
8. **GrassField** - 5400 individual grass blade curves
9. **FaunCharacter** - External PNG image embedded in the scene

## Key Techniques

### Layered Composition

The draw order in `OutdoorScene.draw()` determines what appears in front:

```python
class OutdoorScene(diagram.Diagram):
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
```

### Wavy/Organic Shapes

The horizon line uses a sine wave function for natural undulation:

```python
def get_horizon_y(x):
    wave_amplitude = 8
    return HORIZON_Y + math.sin(x * 0.015) * wave_amplitude
```

### Random Variation

Grass blades have random height, curve, and color for organic appearance:

```python
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

    curves.QuadraticBezier(
        parent=self,
        start=(x, y),
        control=(ctrl_x, ctrl_y),
        end=(end_x, end_y),
        stroke=grass_color,
        stroke_width=random.uniform(0.6, 1.5),
        fill=None,
    )
```

### Color Manipulation

Mountains use opacity and color manipulation for atmospheric perspective:

```python
self._draw_mountain(320, 175, 180, 460, base_y, colors.Color("#9AABB8"), 0.7, 28)  # Far
self._draw_mountain(560, 185, 440, 680, base_y, colors.Color("#8A9BAA"), 0.8, 24)  # Mid
self._draw_mountain(400, 145, 250, 550, base_y, colors.Color("#6B7B8C"), 1.0, 38)  # Near
```

### External Image Embedding

The faun character is an external PNG embedded in the scene:

```python
image.Image(
    parent=self,
    file_path=str(faun_path),
    width=180,
    height=180,
    ll=(480, SCENE_HEIGHT - 30),
)
```

## Running the Example

```bash
python3 docs-examples/outdoor-scene/outdoor_scene.py --render-diagram OutdoorScene
```

To render individual sub-diagrams:

```bash
python3 docs-examples/outdoor-scene/outdoor_scene.py --render-diagram GrassField
python3 docs-examples/outdoor-scene/outdoor_scene.py --render-diagram WoodFrame
```
