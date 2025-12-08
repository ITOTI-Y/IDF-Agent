# YAML Schema Reference

This document provides a complete reference for all YAML fields used in EnergyPlus building configuration.

## Required Sections Overview

| Section | Required | Description |
|---------|----------|-------------|
| SimulationControl | Yes | Simulation parameters |
| Building | Yes | Building metadata |
| Timestep | Yes | Time step configuration |
| Site:Location | Yes | Geographic location |
| RunPeriod | Yes | Simulation period |
| Material | Yes | Building materials |
| Construction | Yes | Material assemblies |
| GlobalGeometryRules | Yes | Coordinate system |
| Zone | Yes | Thermal zones |
| BuildingSurface:Detailed | Yes | Building surfaces |
| FenestrationSurface:Detailed | No | Windows/doors |
| Schedule | Yes | Time schedules |
| HVAC | Yes | HVAC systems |
| Output:* | Yes | Output settings |

---

## SimulationControl

```yaml
SimulationControl:
    Do Zone Sizing Calculation: No          # Yes/No
    Do System Sizing Calculation: No        # Yes/No
    Do Plant Sizing Calculation: No         # Yes/No
    Run Simulation for Sizing Periods: No   # Yes/No
    Run Simulation for Weather File Run Periods: Yes  # Yes/No
    Do HVAC Sizing Simulation for Sizing Periods: Yes # Yes/No (optional)
    Maximum Number of HVAC Sizing Simulation Passes: 1 # int (optional)
```

---

## Building

```yaml
Building:
    Name: string                    # Required, non-empty
    North Axis: float               # 0-359.99, default 0
    Terrain: string                 # Suburbs/City/Country/Ocean/Urban
    Loads Convergence Tolerance Value: float    # >0, default 0.04
    Temperature Convergence Tolerance Value: float  # >0, default 0.4
    Solar Distribution: string      # See options below
    Maximum Number of Warmup Days: int   # >=0, default 25
    Minimum Number of Warmup Days: int   # >=0, default 0
```

**Solar Distribution Options:**
- FullExterior
- MinimalShadowing
- FullInteriorAndExterior
- FullExteriorWithReflections
- FullInteriorAndExteriorWithReflections

---

## Timestep

```yaml
Timestep:
    Number of Timesteps per Hour: int  # >=1, default 4
```

---

## Site:Location

```yaml
Site:Location:
    Name: string         # Required, non-empty
    Latitude: float      # -90 to 90
    Longitude: float     # -180 to 180
    Time Zone: float     # -12 to 14
    Elevation: float     # meters
```

---

## RunPeriod

```yaml
RunPeriod:
    Name: string                    # Required
    Begin Month: int                # 1-12
    Begin Day of Month: int         # 1-31
    Begin Year: int                 # optional
    End Month: int                  # 1-12
    End Day of Month: int           # 1-31
    End Year: int                   # optional
    Day of Week for Start Day: string  # Sunday/Monday/Tuesday/Wednesday/Thursday/Friday/Saturday
    Use Weather File Holidays and Special Days: Yes/No
    Use Weather File Daylight Saving Period: Yes/No
    Apply Weekend Holiday Rule: Yes/No
    Use Weather File Rain Indicators: Yes/No
    Use Weather File Snow Indicators: Yes/No
```

---

## Material

Four types of materials are supported:

### Standard Material
```yaml
Material:
  - Name: string
    Type: Standard
    Roughness: string      # VeryRough/Rough/MediumRough/MediumSmooth/Smooth/VerySmooth
    Thickness: float       # >0, meters
    Conductivity: float    # >0, W/m-K
    Density: float         # >0, kg/m³
    Specific_Heat: float   # >0, J/kg-K
```

### NoMass Material
```yaml
Material:
  - Name: string
    Type: NoMass
    Roughness: string          # Same options as Standard
    Thermal_Resistance: float  # >0, m²-K/W
```

### AirGap Material
```yaml
Material:
  - Name: string
    Type: AirGap
    Thermal_Resistance: float  # >0, m²-K/W
```

### Glazing Material
```yaml
Material:
  - Name: string
    Type: Glazing
    U-Factor: float                      # >0, W/m²-K
    Solar_Heat_Gain_Coefficient: float   # >0
    Visible_Transmittance: float         # 0-1, optional
```

---

## Construction

```yaml
Construction:
  - Name: string
    Layers:           # List of material names, outside to inside
      - MaterialName1
      - MaterialName2
```

**Important:** All materials referenced in Layers must exist in Material section.

---

## GlobalGeometryRules

```yaml
GlobalGeometryRules:
    Starting Vertex Position: string  # UpperLeftCorner/LowerLeftCorner/UpperRightCorner/LowerRightCorner
    Vertex Entry Direction: string    # Counterclockwise/Clockwise
    Coordinate System: string         # World/Relative
```

---

## Zone

```yaml
Zone:
  - Name: string                       # Required, unique
    Direction of Relative North: float # 0-359.99 or null
    X Origin: float                    # meters
    Y Origin: float                    # meters
    Z Origin: float                    # meters
    Type: int                          # >=0, default 1
    Multiplier: int                    # >=1, default 1
    Ceiling Height: float/string       # >0 or "autocalculate"
    Volume: float/string               # >0 or "autocalculate"
    Floor Area: float/string           # >0 or "autocalculate"
```

---

## BuildingSurface:Detailed

```yaml
BuildingSurface:Detailed:
  - Name: string                           # Required, unique
    Surface Type: string                   # Floor/Wall/Ceiling/Roof
    Construction Name: string              # Must exist in Construction
    Zone Name: string                      # Must exist in Zone
    Space Name: null                       # Optional
    Outside Boundary Condition: string     # Ground/Outdoors/Surface/Adiabatic
    Outside Boundary Condition Object: string/null  # Required if OBC=Surface
    Sun Exposure: string                   # SunExposed/NoSun
    Wind Exposure: string                  # WindExposed/NoWind
    View Factor to Ground: float/string    # 0-1 or "autocalculate"
    Vertices:                              # List of 3+ vertices
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
```

**Surface Type to Boundary Condition Mapping:**

| Surface Type | Location | Outside Boundary Condition |
|-------------|----------|---------------------------|
| Floor | Ground level | Ground |
| Floor | Upper level | Surface |
| Roof | Top floor | Outdoors |
| Ceiling | Non-top floor | Surface |
| Wall | Exterior | Outdoors |
| Wall | Interior | Surface |

---

## FenestrationSurface:Detailed

```yaml
FenestrationSurface:Detailed:
  - Name: string                           # Required, unique
    Surface Type: string                   # Window/Door/GlassDoor
    Construction Name: string              # Must exist in Construction
    Building Surface Name: string          # Parent wall surface name
    Outside Boundary Condition Object: null
    View Factor to Ground: float/string    # 0-1 or "autocalculate"
    Frame and Divider Name: null
    Multiplier: int                        # >=1
    Number of Vertices: int/string         # >=3 or "autocalculate"
    Vertices:
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
```

---

## Schedule

### ScheduleTypeLimits
```yaml
Schedule:
  ScheduleTypeLimits:
    - Name: string
      Lower Limit Value: float/""    # number or empty
      Upper Limit Value: float/""    # number or empty
      Numeric Type: string           # CONTINUOUS/DISCRETE
      Unit Type: string              # Dimensionless/Temperature/etc
```

### Schedule:Compact
```yaml
Schedule:
  Schedule:Compact:
    - Name: string
      Schedule Type Limits Name: string  # Must exist in ScheduleTypeLimits
      Data:
        - Through: "MM/DD"       # Must end with "12/31"
          Days:
          - For: "DayType"       # AllDays/Weekdays/Weekends/etc
            Times:
            - Until:
                Time: "HH:MM"    # Last must be "24:00"
                Value: number
```

**Valid Day Types:**
- AllDays
- Weekdays
- Weekends
- Holidays
- SummerDesignDay
- WinterDesignDay
- Sunday/Monday/Tuesday/Wednesday/Thursday/Friday/Saturday

---

## HVAC

### HVACTemplate:Thermostat
```yaml
HVAC:
  HVACTemplate:Thermostat:
    - Name: string
      Heating Setpoint Schedule Name: string  # Must exist in Schedule
      Cooling Setpoint Schedule Name: string  # Must exist in Schedule
```

### HVACTemplate:Zone:IdealLoadsAirSystem
```yaml
HVAC:
  HVACTemplate:Zone:IdealLoadsAirSystem:
    - Zone Name: string                          # Must exist in Zone
      Template Thermostat Name: string           # Must exist in Thermostat
      System Availability Schedule Name: string  # Must exist in Schedule
```

---

## Output Settings

```yaml
Output:VariableDictionary:
    Key Field: string   # regular/IDF

Output:Diagnostics:
    Key 1: string       # DisplayExtraWarnings/etc

Output:Table:SummaryReports:
    Report 1 Name: string  # AllSummary/etc

OutputControl:Table:Style:
    Column Separator: string  # HTML/Comma/Tab/etc
    Unit Conversion: string   # None/JtoKWH/etc

Output:Variable:
  - Key Value: string         # "*" or specific
    Variable Name: string     # EnergyPlus variable name
    Reporting Frequency: string  # Timestep/Hourly/Daily/Monthly/Annual
```
