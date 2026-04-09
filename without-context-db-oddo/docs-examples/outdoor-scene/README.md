# Outdoor Scene Example

This example demonstrates building complex drawings piece by piece using OD-DO
primitives. It showcases layered composition, atmospheric perspective, and
extensive use of curves and random variation.

## Running the Example

```bash
python examples/outdoor-scene/outdoor_scene.py --render-diagram OutdoorScene
```

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

## Key Techniques Demonstrated

### Layered Composition

The draw order in `OutdoorScene.draw()` determines what appears in front:

- Mountains are drawn early so grass covers their bases
- Grass blades are drawn last so they appear in front of everything

### Atmospheric Perspective

Mountains use opacity to create depth:

- Far mountains: 70% opacity, lighter color
- Mid mountains: 80% opacity
- Near mountain: 100% opacity, darker with shadow

### Wavy/Organic Shapes

- Horizon line uses `get_horizon_y(x)` with sine waves
- Snow cap bottoms use bezier curves for irregular edges
- Stream follows `get_stream_y(x)` for natural meandering

### Random Variation

- Grass blades: random height, curve, color (green variations), stroke width
- Mountain texture lines: random position, length, angle
- Stream ripples: random position and size

### External Image Embedding

Uses the new `Image` shape class to embed a PNG file:

```python
image.Image(
    parent=self,
    file_path="monster-faun-greek-flat-by-Vexels.png",
    width=180,
    height=180,
    ll=(480, SCENE_HEIGHT - 30),
)
```

## New OD-DO Features Used

### Image Shape (`od_do.shapes.image`)

Embeds external images (PNG, JPG, SVG) into diagrams:

- Supports positioning via `ll`, `ul`, `lr`, `ur`, or `center`
- Supports `opacity` and `preserve_aspect_ratio`
- Images are base64-encoded into the SVG

## Files

- `outdoor_scene.py` - Main example code
- `outdoor_scene.svg` - Generated output
- `monster-faun-greek-flat-by-Vexels.png` - External image asset
