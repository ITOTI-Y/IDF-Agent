# Error Handling Guide

This document describes common errors during YAML validation and EnergyPlus simulation, along with their fixes.

## Error Detection Workflow

```
1. Generate YAML file
2. Run: python main.py [yaml_file] [epw_file]
3. Check console output for Pydantic validation errors
4. If validation passes, check EnergyPlus output for runtime errors
5. Parse error messages and apply fixes
6. Regenerate YAML and retry (max 3 attempts)
```

---

## Pydantic Validation Errors

### 1. Vertex Count Errors

**Error Message:**
```
ValueError: The surface must have at least 3 vertices. current has X
```

**Cause:** Surface defined with fewer than 3 vertices.

**Fix:**
- Ensure all surfaces have exactly 4 vertices for rectangular surfaces
- Check YAML formatting - vertices may not be parsed correctly

```yaml
# Correct format
Vertices:
  - {X: 0, Y: 0, Z: 0}
  - {X: 5, Y: 0, Z: 0}
  - {X: 5, Y: 5, Z: 0}
  - {X: 0, Y: 5, Z: 0}
```

---

### 2. Vertex Proximity Errors

**Error Message:**
```
ValueError: Some vertices are too close to each other.
Vertices {v1} and {v2} are too close.
```

**Cause:** Two vertices have distance < 1e-10.

**Fix:**
- Round coordinates to reasonable precision (4 decimal places)
- Remove duplicate vertices
- Check for copy-paste errors in vertex definitions

```python
# Auto-fix: Round and deduplicate
def fix_vertices(vertices):
    rounded = []
    seen = set()
    for v in vertices:
        key = (round(v["X"], 4), round(v["Y"], 4), round(v["Z"], 4))
        if key not in seen:
            seen.add(key)
            rounded.append({"X": key[0], "Y": key[1], "Z": key[2]})
    return rounded
```

---

### 3. Geometry Closure Errors

**Error Message:**
```
ValueError: Geometry closure validation failed. Some points are not properly closed.
Point [x, y, z] is not properly closed in the geometry.
```

**Cause:** Surface vertices don't form a closed envelope. Each vertex should appear in at least 3 surfaces.

**Fix:**
- Verify zone is a complete rectangular box (6 surfaces)
- Check that adjacent surfaces share exact vertex coordinates
- Ensure interior wall pairs have matching boundaries

```yaml
# Check that paired surfaces share vertices exactly
Zone_1_Wall_East:
  Vertices:
    - {X: 5, Y: 0, Z: 3}
    - {X: 5, Y: 5, Z: 3}
    - {X: 5, Y: 5, Z: 0}
    - {X: 5, Y: 0, Z: 0}

Zone_2_Wall_West:  # Paired surface - shares same X coordinate
  Vertices:
    - {X: 5, Y: 0, Z: 3}  # Same X=5 plane
    - {X: 5, Y: 5, Z: 3}
    - {X: 5, Y: 5, Z: 0}
    - {X: 5, Y: 0, Z: 0}
```

---

### 4. Reference Not Found Errors

**Error Message:**
```
ValueError: Construction X does not exist
Material X referenced in Construction does not exist
Zone X does not exist
```

**Cause:** Surface, fenestration, or HVAC references a non-existent object.

**Fix:**
- Add missing object definition
- Correct spelling of reference name
- Ensure referenced objects are defined before use

```yaml
# Ensure Material exists before referencing in Construction
Material:
  - Name: Concrete_20cm  # Must exist
    Type: Standard
    ...

Construction:
  - Name: Wall_Const
    Layers:
      - Concrete_20cm  # References Material above
```

---

### 5. Value Range Errors

**Error Messages:**
```
ValueError: North Axis must be in [0, 360)
ValueError: Latitude must be between -90 and 90 degrees
ValueError: Multiplier must be at least 1
ValueError: Value must be positive
```

**Fix:** Adjust value to valid range.

| Field | Valid Range |
|-------|------------|
| North Axis | 0 - 359.99 |
| Latitude | -90 to 90 |
| Longitude | -180 to 180 |
| Time Zone | -12 to 14 |
| Multiplier | >= 1 |
| Thickness | > 0 |
| Conductivity | > 0 |

---

### 6. Boundary Condition Errors

**Error Message:**
```
ValueError: Outside Boundary Condition Object is required when
Outside Boundary Condition is 'Surface'
```

**Cause:** Interior surface missing paired surface reference.

**Fix:**
```yaml
# Interior wall must specify paired surface
- Name: Zone_1_Wall_Interior
  Outside Boundary Condition: Surface
  Outside Boundary Condition Object: Zone_2_Wall_Interior  # Required!
```

---

### 7. Schedule Format Errors

**Error Messages:**
```
ValueError: Schedule data must end with Through: 12/31
ValueError: Last time entry must be 24:00
ValueError: Invalid day type: X
```

**Fix:**
```yaml
Schedule:Compact:
  - Name: My_Schedule
    Schedule Type Limits Name: On/Off
    Data:
      - Through: "12/31"  # Must end with 12/31
        Days:
        - For: "AllDays"  # Valid day type
          Times:
          - Until:
              Time: "24:00"  # Last must be 24:00
              Value: 1
```

---

## EnergyPlus Runtime Errors

After YAML validation passes, EnergyPlus may still report errors. Check the `.err` file in the output directory.

### 1. Surface Geometry Issues

**Error in .err file:**
```
** Severe  ** GetVertices: ...surfaces have incompatible geometry
** Severe  ** Surface="X" has vertex count mismatch
```

**Fix:**
- Regenerate surface vertices with correct ordering
- Ensure vertices are counterclockwise from outside
- Verify normal vectors point outward

---

### 2. Missing Schedule Errors

**Error:**
```
** Severe  ** Schedule "X" not found
** Warning ** GetScheduleInput: Schedule="X" referenced but not found
```

**Fix:**
- Add missing schedule definition
- Check schedule name spelling
- Ensure Schedule Type Limits exist

---

### 3. Uncontrolled Zone Errors

**Error:**
```
** Warning ** Zone "X" is not controlled by any ZoneHVAC equipment
** Severe  ** Zone "X" has no thermostat or HVAC system
```

**Fix:**
- Add HVAC entry for the zone

```yaml
HVAC:
  HVACTemplate:Zone:IdealLoadsAirSystem:
    - Zone Name: X  # Add entry for missing zone
      Template Thermostat Name: Ideal Loads Thermostat
      System Availability Schedule Name: Always On
```

---

### 4. Construction Layer Errors

**Error:**
```
** Severe  ** Construction "X" has invalid layer sequence
** Severe  ** Material "X" in Construction "Y" not found
```

**Fix:**
- Verify all materials exist
- Check layer order (outside to inside)
- Ensure glazing materials only in window constructions

---

### 5. Fatal: Invalid IDF Structure

**Error:**
```
** Fatal  ** Errors occurred on processing input file. Preceding condition(s) cause termination.
** Fatal  ** Could not process input file.
```

**Fix:**
- This is usually a cascading error from earlier issues
- Address all Severe errors first
- Regenerate entire YAML if necessary

---

## Auto-Fix Strategy

```python
def auto_fix_workflow(yaml_data, error_log, max_retries=3):
    """
    Automatically fix errors and retry.
    """
    for attempt in range(max_retries):
        try:
            # Run validation/simulation
            result = run_pipeline(yaml_data)
            if result.success:
                return yaml_data

            error_log = result.errors
        except Exception as e:
            error_log = str(e)

        # Parse and fix errors
        yaml_data = apply_fixes(yaml_data, error_log)

    raise Exception(f"Failed after {max_retries} attempts")

def apply_fixes(yaml_data, error_log):
    """Apply fixes based on error patterns."""

    if "vertices" in error_log.lower():
        yaml_data = fix_vertex_issues(yaml_data, error_log)

    if "closure" in error_log.lower():
        yaml_data = fix_geometry_closure(yaml_data)

    if "not found" in error_log.lower() or "does not exist" in error_log.lower():
        yaml_data = fix_missing_references(yaml_data, error_log)

    if "boundary condition" in error_log.lower():
        yaml_data = fix_boundary_conditions(yaml_data)

    if "schedule" in error_log.lower():
        yaml_data = fix_schedule_issues(yaml_data, error_log)

    if "hvac" in error_log.lower() or "not controlled" in error_log.lower():
        yaml_data = fix_hvac_issues(yaml_data)

    return yaml_data
```

---

## Common Fix Functions

### Fix Vertex Issues
```python
def fix_vertex_issues(yaml_data, error_log):
    """Fix vertex-related errors."""
    surfaces = yaml_data.get("BuildingSurface:Detailed", [])

    for surface in surfaces:
        vertices = surface.get("Vertices", [])

        # Ensure exactly 4 vertices
        if len(vertices) < 4:
            # Regenerate vertices based on zone dimensions
            vertices = regenerate_surface_vertices(surface)

        # Round and deduplicate
        vertices = fix_vertices(vertices)

        surface["Vertices"] = vertices

    return yaml_data
```

### Fix Geometry Closure
```python
def fix_geometry_closure(yaml_data):
    """Fix geometry closure issues."""
    zones = yaml_data.get("Zone", [])
    surfaces = yaml_data.get("BuildingSurface:Detailed", [])

    for zone in zones:
        zone_surfaces = [s for s in surfaces if s["Zone Name"] == zone["Name"]]

        # Check for missing surfaces
        surface_types = [s["Surface Type"] for s in zone_surfaces]

        required = {"Floor", "Roof", "Wall"}  # Minimum required
        missing = required - set(surface_types)

        if missing:
            # Generate missing surfaces
            new_surfaces = generate_missing_surfaces(zone, missing)
            surfaces.extend(new_surfaces)

    yaml_data["BuildingSurface:Detailed"] = surfaces
    return yaml_data
```

### Fix Missing References
```python
def fix_missing_references(yaml_data, error_log):
    """Fix missing object references."""

    # Extract missing object name from error
    import re
    match = re.search(r"['\"]([^'\"]+)['\"].*not found", error_log, re.I)
    if not match:
        return yaml_data

    missing_name = match.group(1)

    # Determine object type and add default
    if "schedule" in error_log.lower():
        yaml_data = add_default_schedule(yaml_data, missing_name)
    elif "material" in error_log.lower():
        yaml_data = add_default_material(yaml_data, missing_name)
    elif "construction" in error_log.lower():
        yaml_data = add_default_construction(yaml_data, missing_name)

    return yaml_data
```

### Fix HVAC Issues
```python
def fix_hvac_issues(yaml_data):
    """Ensure all zones have HVAC."""
    zones = yaml_data.get("Zone", [])
    hvac = yaml_data.get("HVAC", {})

    ideal_loads = hvac.get("HVACTemplate:Zone:IdealLoadsAirSystem", [])
    controlled_zones = {h["Zone Name"] for h in ideal_loads}

    for zone in zones:
        if zone["Name"] not in controlled_zones:
            ideal_loads.append({
                "Zone Name": zone["Name"],
                "Template Thermostat Name": "Ideal Loads Thermostat",
                "System Availability Schedule Name": "Always On"
            })

    hvac["HVACTemplate:Zone:IdealLoadsAirSystem"] = ideal_loads
    yaml_data["HVAC"] = hvac
    return yaml_data
```

---

## Error Log Locations

| Error Type | Location |
|-----------|----------|
| Pydantic Validation | Console stdout/stderr |
| EnergyPlus Errors | `output/results/energyplus_runs_*/eplusout.err` |
| EnergyPlus Warnings | `output/results/energyplus_runs_*/eplusout.err` |
| Conversion Logs | `logs/*.log` |
