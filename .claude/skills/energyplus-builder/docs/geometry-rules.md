# Geometry Calculation Rules

This document defines the rules for calculating building geometry including zone positions, surface vertices, and window placements.

## Coordinate System

```
        Z (up)
        |
        |
        +------ Y (north)
       /
      /
     X (east)

Origin (0,0,0): Southwest corner of ground floor at floor level
```

### Conventions
- **X-axis**: West to East (positive towards East)
- **Y-axis**: South to North (positive towards North)
- **Z-axis**: Down to Up (positive towards sky)
- **GlobalGeometryRules**: UpperLeftCorner, Counterclockwise, World

---

## Building Footprint Calculation

### From Total Area

```python
def calculate_footprint(total_area, num_floors, aspect_ratio=1.5):
    """
    Calculate building footprint dimensions.

    Args:
        total_area: Total building area in m²
        num_floors: Number of floors
        aspect_ratio: Width/Depth ratio (default 1.5)

    Returns:
        width (X dimension), depth (Y dimension)
    """
    floor_area = total_area / num_floors

    # width * depth = floor_area
    # width / depth = aspect_ratio
    # Therefore: width = sqrt(floor_area * aspect_ratio)

    width = math.sqrt(floor_area * aspect_ratio)
    depth = floor_area / width

    return round(width, 2), round(depth, 2)

# Example: 600 m² building, 2 floors, aspect ratio 1.5
# floor_area = 300 m²
# width = sqrt(300 * 1.5) = 21.21 m
# depth = 300 / 21.21 = 14.14 m
```

---

## Zone Subdivision

### Simple Layout (1-3 zones)

```python
def subdivide_simple(width, depth, num_zones):
    """Subdivide floor into 1-3 zones along X-axis."""
    zones = []
    zone_width = width / num_zones

    for i in range(num_zones):
        zone = {
            "name": f"Zone_{i+1}",
            "x_origin": i * zone_width,
            "y_origin": 0,
            "width": zone_width,
            "depth": depth
        }
        zones.append(zone)

    return zones
```

### Medium Layout (Grid Pattern)

```python
def subdivide_medium(width, depth, grid_x, grid_y):
    """
    Subdivide floor into grid pattern.

    Args:
        width, depth: Floor dimensions
        grid_x: Number of zones along X-axis
        grid_y: Number of zones along Y-axis
    """
    zones = []
    zone_width = width / grid_x
    zone_depth = depth / grid_y

    for j in range(grid_y):
        for i in range(grid_x):
            zone = {
                "name": f"Zone_{j * grid_x + i + 1}",
                "x_origin": i * zone_width,
                "y_origin": j * zone_depth,
                "width": zone_width,
                "depth": zone_depth
            }
            zones.append(zone)

    return zones

# Example: 2x3 grid on 20m x 15m floor
# zone_width = 20/2 = 10m
# zone_depth = 15/3 = 5m
```

### Complex Layout (Perimeter + Core)

```python
def subdivide_complex(width, depth, perimeter_depth=4.5):
    """
    Subdivide floor into perimeter + core zones.

    Standard 9-zone layout:
    - 4 corner zones
    - 4 edge zones
    - 1 core zone
    """
    zones = []
    pd = perimeter_depth  # Perimeter depth

    # Calculate core dimensions
    core_width = width - 2 * pd
    core_depth = depth - 2 * pd

    # Corner zones (4)
    corners = [
        ("SW", 0, 0, pd, pd),
        ("SE", width - pd, 0, pd, pd),
        ("NW", 0, depth - pd, pd, pd),
        ("NE", width - pd, depth - pd, pd, pd),
    ]

    # Edge zones (4)
    edges = [
        ("S", pd, 0, core_width, pd),
        ("N", pd, depth - pd, core_width, pd),
        ("W", 0, pd, pd, core_depth),
        ("E", width - pd, pd, pd, core_depth),
    ]

    # Core zone (1)
    core = ("Core", pd, pd, core_width, core_depth)

    # Combine all zones
    for name, x, y, w, d in corners + edges + [core]:
        zones.append({
            "name": f"Perimeter_{name}" if name != "Core" else "Core",
            "x_origin": x,
            "y_origin": y,
            "width": w,
            "depth": d
        })

    return zones
```

---

## Surface Vertex Generation

### Rectangular Zone Surfaces

For a zone at position (x0, y0, z0) with dimensions (w, d, h):

```python
def generate_zone_surfaces(zone_name, x0, y0, z0, w, d, h,
                           floor_below=None, ceiling_above=None,
                           walls_exterior=None):
    """
    Generate all surfaces for a rectangular zone.

    Args:
        zone_name: Name of the zone
        x0, y0, z0: Zone origin coordinates
        w, d, h: Zone width, depth, height
        floor_below: Name of floor surface below (for Surface BC)
        ceiling_above: Name of ceiling surface above (for Surface BC)
        walls_exterior: Dict of {direction: True/False} for exterior walls
    """
    surfaces = []

    # Floor
    floor = {
        "Name": f"{zone_name}_Floor",
        "Surface Type": "Floor",
        "Zone Name": zone_name,
        "Outside Boundary Condition": "Ground" if z0 == 0 else "Surface",
        "Outside Boundary Condition Object": floor_below,
        "Sun Exposure": "NoSun",
        "Wind Exposure": "NoWind",
        "Vertices": [
            {"X": x0,     "Y": y0 + d, "Z": z0},  # Upper Left
            {"X": x0 + w, "Y": y0 + d, "Z": z0},  # Upper Right
            {"X": x0 + w, "Y": y0,     "Z": z0},  # Lower Right
            {"X": x0,     "Y": y0,     "Z": z0},  # Lower Left
        ]
    }
    surfaces.append(floor)

    # Roof/Ceiling
    is_roof = ceiling_above is None
    ceiling = {
        "Name": f"{zone_name}_{'Roof' if is_roof else 'Ceiling'}",
        "Surface Type": "Roof" if is_roof else "Ceiling",
        "Zone Name": zone_name,
        "Outside Boundary Condition": "Outdoors" if is_roof else "Surface",
        "Outside Boundary Condition Object": ceiling_above,
        "Sun Exposure": "SunExposed" if is_roof else "NoSun",
        "Wind Exposure": "WindExposed" if is_roof else "NoWind",
        "Vertices": [
            {"X": x0,     "Y": y0,     "Z": z0 + h},
            {"X": x0 + w, "Y": y0,     "Z": z0 + h},
            {"X": x0 + w, "Y": y0 + d, "Z": z0 + h},
            {"X": x0,     "Y": y0 + d, "Z": z0 + h},
        ]
    }
    surfaces.append(ceiling)

    # Walls
    walls_exterior = walls_exterior or {"N": True, "S": True, "E": True, "W": True}

    # North Wall (Y = y0 + d)
    north_wall = generate_wall(
        f"{zone_name}_Wall_North", zone_name,
        [(x0 + w, y0 + d, z0 + h), (x0 + w, y0 + d, z0),
         (x0, y0 + d, z0), (x0, y0 + d, z0 + h)],
        is_exterior=walls_exterior.get("N", True)
    )
    surfaces.append(north_wall)

    # South Wall (Y = y0)
    south_wall = generate_wall(
        f"{zone_name}_Wall_South", zone_name,
        [(x0, y0, z0), (x0 + w, y0, z0),
         (x0 + w, y0, z0 + h), (x0, y0, z0 + h)],
        is_exterior=walls_exterior.get("S", True)
    )
    surfaces.append(south_wall)

    # East Wall (X = x0 + w)
    east_wall = generate_wall(
        f"{zone_name}_Wall_East", zone_name,
        [(x0 + w, y0, z0), (x0 + w, y0 + d, z0),
         (x0 + w, y0 + d, z0 + h), (x0 + w, y0, z0 + h)],
        is_exterior=walls_exterior.get("E", True)
    )
    surfaces.append(east_wall)

    # West Wall (X = x0)
    west_wall = generate_wall(
        f"{zone_name}_Wall_West", zone_name,
        [(x0, y0, z0 + h), (x0, y0 + d, z0 + h),
         (x0, y0 + d, z0), (x0, y0, z0)],
        is_exterior=walls_exterior.get("W", True)
    )
    surfaces.append(west_wall)

    return surfaces

def generate_wall(name, zone_name, vertices_list, is_exterior=True):
    """Generate a wall surface."""
    return {
        "Name": name,
        "Surface Type": "Wall",
        "Zone Name": zone_name,
        "Outside Boundary Condition": "Outdoors" if is_exterior else "Surface",
        "Outside Boundary Condition Object": None,  # Set later for interior
        "Sun Exposure": "SunExposed" if is_exterior else "NoSun",
        "Wind Exposure": "WindExposed" if is_exterior else "NoWind",
        "Vertices": [{"X": v[0], "Y": v[1], "Z": v[2]} for v in vertices_list]
    }
```

---

## Wall Vertex Order

Vertices must be in **counterclockwise order when viewed from outside the zone**.

### North Wall (Y = y_max, normal points +Y)
```
Looking from outside (from +Y direction toward -Y):
    TL -------- TR
    |          |
    |  (wall)  |
    |          |
    BL -------- BR

Counterclockwise from UpperLeft: TR → BR → BL → TL
Vertices: [(x+w, y+d, z+h), (x+w, y+d, z), (x, y+d, z), (x, y+d, z+h)]
```

### South Wall (Y = y_min, normal points -Y)
```
Looking from outside (from -Y direction toward +Y):
    TR -------- TL
    |          |
    |  (wall)  |
    |          |
    BR -------- BL

Counterclockwise from UpperLeft: BL → BR → TR → TL
Vertices: [(x, y, z), (x+w, y, z), (x+w, y, z+h), (x, y, z+h)]
```

### East Wall (X = x_max, normal points +X)
```
Looking from outside (from +X direction toward -X):
    TL -------- TR
    |          |
    |  (wall)  |
    |          |
    BL -------- BR

Counterclockwise: BR → TR → TL → BL
Vertices: [(x+w, y, z), (x+w, y+d, z), (x+w, y+d, z+h), (x+w, y, z+h)]
```

### West Wall (X = x_min, normal points -X)
```
Looking from outside (from -X direction toward +X):
    TR -------- TL
    |          |
    |  (wall)  |
    |          |
    BR -------- BL

Counterclockwise: TL → TR → BR → BL
Vertices: [(x, y, z+h), (x, y+d, z+h), (x, y+d, z), (x, y, z)]
```

---

## Window Placement

### Single Window on Wall

```python
def place_window_on_wall(wall_name, wall_vertices, wwr=0.30, sill_height=0.9):
    """
    Place a window centered on a wall surface.

    Args:
        wall_name: Parent wall surface name
        wall_vertices: List of wall vertex coordinates
        wwr: Window-to-Wall Ratio (0.0-1.0)
        sill_height: Height from floor to window bottom (m)
    """
    # Calculate wall dimensions from vertices
    # Assuming rectangular wall with 4 vertices

    # Find wall plane and dimensions
    v = wall_vertices

    # Calculate wall width (horizontal extent)
    # Wall width is along the horizontal direction
    dx = max(p["X"] for p in v) - min(p["X"] for p in v)
    dy = max(p["Y"] for p in v) - min(p["Y"] for p in v)
    wall_width = max(dx, dy)  # Horizontal extent

    # Wall height (vertical extent)
    wall_height = max(p["Z"] for p in v) - min(p["Z"] for p in v)

    # Calculate window dimensions
    wall_area = wall_width * wall_height
    window_area = wall_area * wwr

    # Typical window aspect ratio (width/height = 1.5)
    window_aspect = 1.5
    window_height = math.sqrt(window_area / window_aspect)
    window_width = window_height * window_aspect

    # Constraints
    min_edge_margin = 0.3  # Minimum distance from wall edge
    max_window_height = wall_height - sill_height - 0.3  # Leave top margin

    # Adjust if necessary
    window_height = min(window_height, max_window_height)
    window_width = min(window_width, wall_width - 2 * min_edge_margin)

    # Center window on wall
    h_offset = (wall_width - window_width) / 2
    z_bottom = min(p["Z"] for p in v) + sill_height
    z_top = z_bottom + window_height

    # Generate window vertices based on wall orientation
    # (Implementation depends on wall direction)

    return window_vertices
```

### Window Vertices for Different Wall Orientations

```python
# North Wall Window (Y = y_max)
# Window is on plane Y = y_max, extends in X and Z
window_north = [
    {"X": x_center + win_w/2, "Y": y_max, "Z": z_top},
    {"X": x_center + win_w/2, "Y": y_max, "Z": z_bottom},
    {"X": x_center - win_w/2, "Y": y_max, "Z": z_bottom},
    {"X": x_center - win_w/2, "Y": y_max, "Z": z_top},
]

# South Wall Window (Y = y_min)
window_south = [
    {"X": x_center - win_w/2, "Y": y_min, "Z": z_bottom},
    {"X": x_center + win_w/2, "Y": y_min, "Z": z_bottom},
    {"X": x_center + win_w/2, "Y": y_min, "Z": z_top},
    {"X": x_center - win_w/2, "Y": y_min, "Z": z_top},
]

# East Wall Window (X = x_max)
window_east = [
    {"X": x_max, "Y": y_center - win_w/2, "Z": z_bottom},
    {"X": x_max, "Y": y_center + win_w/2, "Z": z_bottom},
    {"X": x_max, "Y": y_center + win_w/2, "Z": z_top},
    {"X": x_max, "Y": y_center - win_w/2, "Z": z_top},
]

# West Wall Window (X = x_min)
window_west = [
    {"X": x_min, "Y": y_center - win_w/2, "Z": z_top},
    {"X": x_min, "Y": y_center + win_w/2, "Z": z_top},
    {"X": x_min, "Y": y_center + win_w/2, "Z": z_bottom},
    {"X": x_min, "Y": y_center - win_w/2, "Z": z_bottom},
]
```

---

## Multi-Floor Geometry

### Floor Origin Calculation

```python
def calculate_floor_origins(num_floors, floor_height):
    """Calculate Z origins for each floor."""
    return [floor_height * i for i in range(num_floors)]

# Example: 3 floors, 3.5m height each
# Floor 1: z_origin = 0
# Floor 2: z_origin = 3.5
# Floor 3: z_origin = 7.0
```

### Floor/Ceiling Pairing

```python
def create_floor_ceiling_pairs(zones_by_floor):
    """
    Create floor/ceiling surface pairs between floors.

    Args:
        zones_by_floor: Dict of {floor_num: [zone_list]}
    """
    pairs = []
    num_floors = len(zones_by_floor)

    for floor in range(1, num_floors):
        lower_floor = floor - 1

        for lower_zone in zones_by_floor[lower_floor]:
            # Find corresponding zone on upper floor
            # (assumes same zone layout per floor)
            upper_zone = find_matching_zone(
                lower_zone,
                zones_by_floor[floor]
            )

            if upper_zone:
                ceiling_name = f"F{lower_floor+1}_{lower_zone['name']}_Ceiling"
                floor_name = f"F{floor+1}_{upper_zone['name']}_Floor"

                pairs.append({
                    "ceiling": ceiling_name,
                    "floor": floor_name,
                })

    return pairs
```

---

## Geometry Validation

### Closure Check

All zones must form closed volumes. Each vertex should appear in exactly 3 surfaces (for rectangular zones).

```python
def validate_closure(surfaces):
    """
    Validate that surfaces form a closed geometry.

    Each unique vertex should appear in exactly 3 surfaces
    (meeting at a corner of a rectangular zone).
    """
    vertex_counts = {}

    for surface in surfaces:
        for v in surface["Vertices"]:
            key = (round(v["X"], 8), round(v["Y"], 8), round(v["Z"], 8))
            vertex_counts[key] = vertex_counts.get(key, 0) + 1

    # Check all vertices appear at least 3 times
    unclosed = [v for v, count in vertex_counts.items() if count < 3]

    if unclosed:
        raise ValueError(f"Geometry not closed at vertices: {unclosed}")

    return True
```

### Vertex Distance Check

```python
def validate_vertex_distances(vertices, min_distance=1e-10):
    """Ensure no two vertices are too close."""
    for i, v1 in enumerate(vertices):
        for j, v2 in enumerate(vertices[i+1:], i+1):
            distance = math.sqrt(
                (v1["X"] - v2["X"])**2 +
                (v1["Y"] - v2["Y"])**2 +
                (v1["Z"] - v2["Z"])**2
            )
            if distance < min_distance:
                raise ValueError(f"Vertices {i} and {j} too close: {distance}")
    return True
```
