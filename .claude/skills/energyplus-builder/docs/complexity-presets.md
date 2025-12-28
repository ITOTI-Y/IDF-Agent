# Complexity Presets

This document defines the building configurations for each complexity level.

## Overview

| Level | Zones/Floor | Windows/Wall | Interior Walls | Default Area/Zone | Ceiling Height |
|-------|-------------|--------------|----------------|-------------------|----------------|
| Simple | 1-3 | 0-1 | No | 100 m² | 3.0 m |
| Medium | 4-8 | 1-2 | Yes | 50 m² | 3.2 m |
| Complex | 9+ | 2-3 | Yes + Doors | 30 m² | 3.5 m |

---

## Simple Complexity (每层最多3个热区)

### Characteristics
- **Zone count**: 1-3 zones per floor
- **Layout pattern**: Single zone or linear divisions along one axis
- **Windows**: 0-1 window per exterior wall
- **Interior walls**: None (open floor plan) or simple partitions
- **Typical use cases**: Small residential, single-room buildings

### Zone Layout Patterns

#### Pattern 1: Single Zone (1 zone)
```
+------------------+
|                  |
|     Zone_1       |
|                  |
+------------------+
```

#### Pattern 2: Two Zones (2 zones)
```
+--------+---------+
|        |         |
| Zone_1 | Zone_2  |
|        |         |
+--------+---------+
```

#### Pattern 3: Three Zones (3 zones)
```
+------+------+------+
|      |      |      |
| Z_1  | Z_2  | Z_3  |
|      |      |      |
+------+------+------+
```

### Default Configuration

```yaml
# Simple building defaults
complexity: simple
zones_per_floor: 1-3
default_zone_dimensions:
  area: 100  # m²
  aspect_ratio: 1.5  # width/depth
  ceiling_height: 3.0  # m

window_config:
  windows_per_exterior_wall: 1
  window_wall_ratio: 0.25
  sill_height: 0.9  # m

materials:
  exterior_wall: Concrete_20cm
  interior_wall: null  # No interior walls
  roof: Concrete_20cm
  floor: Concrete_20cm
  window: SimpleGlazingSystem
```

---

## Medium Complexity (每层最多8个热区和8个门窗)

### Characteristics
- **Zone count**: 4-8 zones per floor
- **Layout pattern**: Grid pattern (2×2, 2×3, 2×4)
- **Windows**: 1-2 windows per exterior wall
- **Interior walls**: Gypsum board partitions
- **Typical use cases**: Small office, retail, multi-room residential

### Zone Layout Patterns

#### Pattern 1: 2×2 Grid (4 zones)
```
+--------+---------+
| Zone_1 | Zone_2  |
+--------+---------+
| Zone_3 | Zone_4  |
+--------+---------+
```

#### Pattern 2: 2×3 Grid (6 zones)
```
+------+------+------+
| Z_1  | Z_2  | Z_3  |
+------+------+------+
| Z_4  | Z_5  | Z_6  |
+------+------+------+
```

#### Pattern 3: 2×4 Grid (8 zones)
```
+----+----+----+----+
| Z1 | Z2 | Z3 | Z4 |
+----+----+----+----+
| Z5 | Z6 | Z7 | Z8 |
+----+----+----+----+
```

### Default Configuration

```yaml
# Medium building defaults
complexity: medium
zones_per_floor: 4-8
default_zone_dimensions:
  area: 50  # m²
  aspect_ratio: 1.2
  ceiling_height: 3.2  # m

window_config:
  windows_per_exterior_wall: 1-2
  window_wall_ratio: 0.30
  sill_height: 0.9  # m

materials:
  exterior_wall: Concrete_20cm
  interior_wall: Interior_Wall_Const  # Gypsum_1.3cm + Gypsum_1.3cm
  roof: Concrete_20cm
  floor: Concrete_20cm
  window: SimpleGlazingSystem

interior_wall_config:
  boundary_condition: Surface
  sun_exposure: NoSun
  wind_exposure: NoWind
```

### Interior Wall Pairing

For medium complexity, interior walls must be paired:

```yaml
# Zone_1 to Zone_2 interior wall
- Name: Zone_1_Wall_Interior_East
  Outside Boundary Condition: Surface
  Outside Boundary Condition Object: Zone_2_Wall_Interior_West

# Zone_2 to Zone_1 interior wall (paired)
- Name: Zone_2_Wall_Interior_West
  Outside Boundary Condition: Surface
  Outside Boundary Condition Object: Zone_1_Wall_Interior_East
```

---

## Complex Complexity (多热区及多门窗)

### Characteristics
- **Zone count**: 9+ zones per floor
- **Layout pattern**: Perimeter zones + core zones
- **Windows**: 2-3 windows per exterior wall, varied sizes
- **Interior walls**: Full partitioning with doors
- **Typical use cases**: Large office, commercial, institutional

### Zone Layout Pattern: Perimeter + Core

```
+-------+-------+-------+
| NW    | North | NE    |  <- Perimeter zones (exterior exposure)
+-------+-------+-------+
| West  | Core1 | East  |  <- Core zones (interior only)
+-------+-------+-------+
| SW    | South | SE    |  <- Perimeter zones
+-------+-------+-------+
```

### Detailed 9-Zone Layout

```
Zone naming convention:
- Perimeter zones: Floor{N}_Perimeter_{Direction}
- Core zones: Floor{N}_Core

Floor 1 layout:
+------------------+------------------+------------------+
| F1_Perimeter_NW  | F1_Perimeter_N   | F1_Perimeter_NE  |
+------------------+------------------+------------------+
| F1_Perimeter_W   | F1_Core          | F1_Perimeter_E   |
+------------------+------------------+------------------+
| F1_Perimeter_SW  | F1_Perimeter_S   | F1_Perimeter_SE  |
+------------------+------------------+------------------+
```

### Default Configuration

```yaml
# Complex building defaults
complexity: complex
zones_per_floor: 9+
default_zone_dimensions:
  perimeter_depth: 4.5  # m (distance from exterior wall)
  core_area: variable
  ceiling_height: 3.5  # m

window_config:
  windows_per_exterior_wall: 2-3
  window_wall_ratio: 0.40
  sill_height: 0.8  # m
  varied_sizes: true

materials:
  exterior_wall: Concrete_20cm
  interior_wall: Interior_Wall_Const
  roof: Concrete_20cm
  floor: Concrete_20cm
  ceiling: Ceiling_Const
  window: SimpleGlazingSystem

interior_wall_config:
  boundary_condition: Surface
  sun_exposure: NoSun
  wind_exposure: NoWind

# Multi-floor configuration
multi_floor:
  floor_to_floor_height: 3.5  # m
  intermediate_floor_surface: Surface  # Ceiling/Floor pairs
```

### Multi-Floor Zone Naming

For multi-story complex buildings:

```
Floor 1: F1_Perimeter_N, F1_Perimeter_E, F1_Core, etc.
Floor 2: F2_Perimeter_N, F2_Perimeter_E, F2_Core, etc.
Floor 3: F3_Perimeter_N, F3_Perimeter_E, F3_Core, etc.
```

### Floor/Ceiling Pairing Between Floors

```yaml
# Floor 1 Roof (top surface)
- Name: F1_Core_Ceiling
  Surface Type: Ceiling
  Outside Boundary Condition: Surface
  Outside Boundary Condition Object: F2_Core_Floor

# Floor 2 Floor (bottom surface - paired)
- Name: F2_Core_Floor
  Surface Type: Floor
  Outside Boundary Condition: Surface
  Outside Boundary Condition Object: F1_Core_Ceiling
```

---

## Complexity Selection Algorithm

```python
def select_complexity(user_input):
    """
    Select complexity level based on user input.

    Priority:
    1. Explicit complexity specification
    2. Zone count indicators
    3. Building type defaults
    4. Default to medium
    """

    # Check for explicit complexity
    if "simple" in user_input.lower():
        return "simple"
    if "complex" in user_input.lower():
        return "complex"
    if "medium" in user_input.lower():
        return "medium"

    # Check zone indicators
    zones = extract_zone_count(user_input)
    if zones:
        if zones <= 3:
            return "simple"
        elif zones <= 8:
            return "medium"
        else:
            return "complex"

    # Building type defaults
    building_type = extract_building_type(user_input)
    type_defaults = {
        "residential": "simple",
        "small_office": "medium",
        "large_office": "complex",
        "commercial": "medium",
        "industrial": "simple",
    }

    return type_defaults.get(building_type, "medium")
```

---

## Zone Count Calculation

```python
def calculate_zone_count(complexity, num_floors, total_area=None):
    """Calculate number of zones based on complexity."""

    presets = {
        "simple": {"zones_per_floor": 1, "max_zones_per_floor": 3},
        "medium": {"zones_per_floor": 4, "max_zones_per_floor": 8},
        "complex": {"zones_per_floor": 9, "max_zones_per_floor": 16},
    }

    preset = presets[complexity]
    zones_per_floor = preset["zones_per_floor"]

    # Adjust based on area if provided
    if total_area:
        floor_area = total_area / num_floors

        if complexity == "simple":
            # 1 zone per 100m²
            zones_per_floor = min(max(1, floor_area // 100), 3)
        elif complexity == "medium":
            # 1 zone per 50m²
            zones_per_floor = min(max(4, floor_area // 50), 8)
        else:
            # 1 zone per 30m²
            zones_per_floor = min(max(9, floor_area // 30), 16)

    total_zones = zones_per_floor * num_floors
    return int(zones_per_floor), int(total_zones)
```
