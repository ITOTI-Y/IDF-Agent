---
name: energyplus-builder
description: "Generate EnergyPlus building simulations from natural language descriptions or building images. Use when user asks to 'create building simulation', 'generate IDF', 'simulate X-story building', provides building floor plans, 3D models, or describes buildings like 'a 3-story office building in Shenzhen'."
---

# EnergyPlus Building Simulation Skill

This skill automates the complete workflow from building description to EnergyPlus simulation results.

## Capabilities

1. Parse natural language building descriptions (Chinese/English)
2. Analyze building images (floor plans, 3D models) for geometry extraction
3. Generate compliant YAML configuration files
4. Execute YAML-to-IDF conversion with Pydantic validation
5. Run EnergyPlus simulations
6. Detect and auto-fix common errors
7. Output clean, validated YAML files

---

## Required User Inputs (必需的用户输入)

在生成建筑模拟前，必须明确以下参数。如果用户未提供，应主动询问：

### 1. 核心几何参数 (Core Geometry Parameters)

| 参数 | 描述 | 示例值 | 是否必需 |
|-----|------|-------|---------|
| `num_floors` | 楼层数 | 1, 2, 3... | **必需** |
| `floor_dimensions` | 每层平面尺寸 (长×宽) | 10m × 5m | **必需** (或提供 `total_area`) |
| `total_area` | 总建筑面积 | 500 m² | **必需** (如未提供 `floor_dimensions`) |
| `ceiling_height` | 层高 | 3.0 m | 可选 (默认 3.0m) |

### 2. 位置参数 (Location Parameters)

| 参数 | 描述 | 示例值 | 是否必需 |
|-----|------|-------|---------|
| `location` | 城市/地点 | Shenzhen, Beijing | **必需** |
| `north_axis` | 建筑朝向角度 | 0 (正北), 45, 90... | 可选 (默认 0) |

### 3. 热区划分参数 (Zone Division Parameters)

| 参数 | 描述 | 示例值 | 是否必需 |
|-----|------|-------|---------|
| `complexity` | 复杂度级别 | simple/medium/complex | 可选 (默认 medium) |
| `zones_per_floor` | 每层热区数 | 1, 2, 4... | 可选 (根据 complexity 自动推断) |
| `zone_layout` | 热区布局方式 | single/linear/grid/perimeter-core | 可选 |

### 4. 围护结构参数 (Envelope Parameters)

| 参数 | 描述 | 示例值 | 是否必需 |
|-----|------|-------|---------|
| `has_windows` | 是否有窗户 | true/false | 可选 (默认 true) |
| `window_wall_ratio` | 窗墙比 | 0.3 (30%) | 可选 (默认 0.3) |
| `wall_construction` | 外墙构造 | 20cm混凝土 | 可选 (使用默认) |

### 5. HVAC 参数 (HVAC Parameters)

| 参数 | 描述 | 示例值 | 是否必需 |
|-----|------|-------|---------|
| `hvac_type` | HVAC类型 | IdealLoads | 可选 (默认 IdealLoads) |
| `heating_setpoint` | 供暖设定温度 | 20°C | 可选 (默认 20°C) |
| `cooling_setpoint` | 制冷设定温度 | 26°C | 可选 (默认 26°C) |

---

## Input Types (输入类型)

### Natural Language Examples (自然语言示例)
```
"一栋三层的办公楼，每层10米×15米，层高3.2米，位于深圳"
"A 2-story residential building, 8m x 6m per floor, in Beijing"
"Create a simple 1-floor building, 20m x 10m, with 2 zones"
```

### 必须询问用户的情况
当用户输入缺少以下信息时，必须主动询问：
1. **楼层数未指定**: "请问建筑有几层？"
2. **尺寸未指定**: "请问每层的平面尺寸是多少？(长×宽)"
3. **位置未指定**: "请问建筑位于哪个城市？"

### Image Types Supported (支持的图像类型)
- Floor plans (平面图)
- 3D building models/renderings (3D模型/渲染图)
- CAD exports (CAD导出图)

---

## Complexity Levels (复杂度级别)

### Simple (简单 - 每层最多3个热区)
```
Zones per floor: 1-3
Layout: Single zone or linear divisions (单区域或线性划分)
Windows per exterior wall: 0-1
Default zone area: 100 m²
Ceiling height: 3.0 m
Interior walls: None between zones
```

### Medium (中等 - 每层最多8个热区)
```
Zones per floor: 4-8
Layout: Grid pattern (2x2, 2x3, 2x4) (网格布局)
Windows per exterior wall: 1-2
Default zone area: 50 m²
Ceiling height: 3.2 m
Interior walls: Yes, between zones
```

### Complex (复杂 - 多热区)
```
Zones per floor: 9+
Layout: Perimeter + core pattern (周边+核心布局)
Windows per exterior wall: 2-3
Default zone area: 30 m²
Ceiling height: 3.5 m
Interior walls: Yes, with doors
```

---

## City Location Database (城市位置数据库)

```yaml
Shenzhen/深圳:
  Name: Shenzhen_GD_CHN Design_Conditions
  Latitude: 22.54
  Longitude: 114.00
  Time Zone: 8.00
  Elevation: 4.00

Beijing/北京:
  Name: Beijing_CHN Design_Conditions
  Latitude: 39.92
  Longitude: 116.46
  Time Zone: 8.00
  Elevation: 55.00

Shanghai/上海:
  Name: Shanghai_CHN Design_Conditions
  Latitude: 31.17
  Longitude: 121.43
  Time Zone: 8.00
  Elevation: 4.00

Guangzhou/广州:
  Name: Guangzhou_GD_CHN Design_Conditions
  Latitude: 23.13
  Longitude: 113.32
  Time Zone: 8.00
  Elevation: 11.00
```

---

## Workflow Instructions (工作流程)

### Step 1: Parse User Input & Validate Requirements

1. Extract building parameters from natural language or image
2. **检查必需参数是否完整**:
   - 如果缺少楼层数 → 询问用户
   - 如果缺少尺寸/面积 → 询问用户
   - 如果缺少位置 → 询问用户
3. Determine complexity level (simple/medium/complex)
4. Set defaults for optional parameters

### Step 2: Calculate Building Geometry

Use the geometry rules from `./docs/geometry-rules.md`:

1. Calculate building footprint based on dimensions or total area
2. Subdivide into zones based on complexity level
3. Generate surface vertices for each zone (floor, ceiling/roof, walls)
4. Calculate window positions for exterior walls

### Step 3: Generate YAML File

Generate YAML following the structure in `./docs/yaml-schema-reference.md`.

**Required sections in order:**
```yaml
SimulationControl:      # 模拟控制
Building:               # 建筑信息
Timestep:               # 时间步长
Site:Location:          # 场地位置
RunPeriod:              # 运行周期
Material:               # 材料定义
Construction:           # 构造定义
GlobalGeometryRules:    # 几何规则
Zone:                   # 热区定义
BuildingSurface:Detailed:  # 建筑表面
FenestrationSurface:Detailed:  # 门窗 (可选)
Schedule:               # 时间表
HVAC:                   # 暖通系统
Output:VariableDictionary:    # 输出设置
Output:Diagnostics:
Output:Table:SummaryReports:
OutputControl:Table:Style:
Output:Variable:
```

Save to: `schemas/generated_building_YYYYMMDD_HHMMSS.yaml`

### Step 4: Execute Pipeline

```bash
python main.py schemas/generated_building_XXXXXX.yaml dependencies/Shenzhen.epw
```

### Step 5: Check for Errors

1. **Pydantic Validation Errors**: Check console output
2. **EnergyPlus Errors**: Check `.err` files in `output/results/energyplus_runs_*/`

See `./docs/error-handling.md` for common error patterns.

### Step 6: Auto-Fix and Retry

Maximum 3 retries with automatic error correction.

### Step 7: Output Results

1. Report simulation success and output location
2. Clean the final YAML file
3. Present the validated YAML to user

---

## YAML Schema Quick Reference (YAML格式速查)

### Schedule Section (时间表部分) - 重要格式说明

Schedule 部分采用嵌套结构，包含两个子部分：

```yaml
Schedule:
  # 1. 时间表类型限制定义
  ScheduleTypeLimits:
    - Name: On/Off                    # 开关类型
      Lower Limit Value: 0            # 下限
      Upper Limit Value: 1            # 上限
      Numeric Type: DISCRETE          # 离散型
      Unit Type: Dimensionless        # 无量纲
      
    - Name: Temperature               # 温度类型
      Numeric Type: CONTINUOUS        # 连续型
      Unit Type: Temperature          # 温度单位
      # Lower/Upper Limit Value 可省略

  # 2. 紧凑格式时间表
  Schedule:Compact:
    - Name: Always On                 # 时间表名称
      Schedule Type Limits Name: On/Off  # 引用类型限制
      Data:                           # 数据部分 - 嵌套结构
        - Through: "12/31"            # 日期范围 (必须以12/31结束)
          Days:                       # 天类型定义
          - For: "AllDays"            # 适用天类型
            Times:                    # 时间-值对
            - Until:
                Time: "24:00"         # 时间点 (最后必须是24:00)
                Value: 1              # 对应值

    - Name: Heating_Setpoint_Schedule
      Schedule Type Limits Name: Temperature
      Data:
        - Through: "12/31"
          Days:
          - For: "AllDays"
            Times:
            - Until:
                Time: "24:00"
                Value: 20             # 供暖设定温度

    - Name: Cooling_Setpoint_Schedule
      Schedule Type Limits Name: Temperature
      Data:
        - Through: "12/31"
          Days:
          - For: "AllDays"
            Times:
            - Until:
                Time: "24:00"
                Value: 26             # 制冷设定温度
```

### Schedule 格式验证规则

1. **ScheduleTypeLimits 字段**:
   - `Name`: 必需，唯一标识符
   - `Lower Limit Value`: 可选，数值或省略
   - `Upper Limit Value`: 可选，数值或省略
   - `Numeric Type`: 必需，`DISCRETE` 或 `CONTINUOUS`
   - `Unit Type`: 必需，如 `Dimensionless`, `Temperature`, `Power` 等

2. **Schedule:Compact Data 结构**:
   ```
   Data (列表)
   └── Through: "MM/DD"        # 日期截止点
       └── Days (列表)
           └── For: "DayType"  # 天类型
               └── Times (列表)
                   └── Until:
                       ├── Time: "HH:MM"
                       └── Value: number
   ```

3. **有效的 Day Types**:
   - `AllDays`, `Weekdays`, `Weekends`, `Holidays`
   - `SummerDesignDay`, `WinterDesignDay`
   - `Sunday`, `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`

4. **关键验证规则**:
   - 最后一个 `Through` 必须是 `"12/31"`
   - 每个 `Days` 块的最后一个 `Time` 必须是 `"24:00"`
   - `Schedule Type Limits Name` 必须引用已定义的 ScheduleTypeLimits

---

### Material Section (材料部分)

支持四种材料类型：

```yaml
Material:
  # 1. Standard - 标准材料 (有厚度)
  - Name: Concrete_20cm
    Type: Standard
    Roughness: MediumRough           # VeryRough/Rough/MediumRough/MediumSmooth/Smooth/VerySmooth
    Thickness: 0.2                   # 厚度 (m)
    Conductivity: 1.729              # 导热系数 (W/m-K)
    Density: 2240                    # 密度 (kg/m³)
    Specific_Heat: 837               # 比热 (J/kg-K)

  # 2. NoMass - 无质量材料 (仅热阻)
  - Name: Interior_Insulation
    Type: NoMass
    Roughness: MediumRough
    Thermal_Resistance: 2.5          # 热阻 (m²-K/W)

  # 3. AirGap - 空气层
  - Name: Roof_AirGap
    Type: AirGap
    Thermal_Resistance: 0.18         # 热阻 (m²-K/W)

  # 4. Glazing - 玻璃材料
  - Name: SimpleGlazingSystem
    Type: Glazing
    U-Factor: 5.8                    # 传热系数 (W/m²-K)
    Solar_Heat_Gain_Coefficient: 0.8 # 太阳得热系数
    Visible_Transmittance: 0.9       # 可见光透射率 (可选)
```

---

### Zone Section (热区部分)

```yaml
Zone:
  - Name: Zone_West                  # 必需，唯一名称
    Direction of Relative North: null  # 相对北向角度 (null 或 0-359.99)
    X Origin: 0                      # X原点 (m)
    Y Origin: 5                      # Y原点 (m)
    Z Origin: 0                      # Z原点 (m) - 楼层高度
    Type: 1                          # 热区类型 (默认 1)
    Multiplier: 1                    # 乘数 (默认 1)
    Ceiling Height: autocalculate    # 层高 (数值或 autocalculate)
    Volume: autocalculate            # 体积 (数值或 autocalculate)
    Floor Area: autocalculate        # 地面积 (数值或 autocalculate)
```

---

### BuildingSurface:Detailed Section (建筑表面部分)

```yaml
BuildingSurface:Detailed:
  - Name: Zone_West_Floor            # 必需，唯一名称
    Surface Type: Floor              # Floor/Wall/Ceiling/Roof
    Construction Name: Floor_Const   # 必须引用已定义的 Construction
    Zone Name: Zone_West             # 必须引用已定义的 Zone
    Space Name: null                 # 可选
    Outside Boundary Condition: Ground  # Ground/Outdoors/Surface/Adiabatic
    Outside Boundary Condition Object: null  # 如果 OBC=Surface，则必需
    Sun Exposure: NoSun              # SunExposed/NoSun
    Wind Exposure: NoWind            # WindExposed/NoWind
    View Factor to Ground: autocalculate  # 0-1 或 autocalculate
    Vertices:                        # 顶点列表 (逆时针，从外部看)
      - {X: 0, Y: 5, Z: 0}
      - {X: 5, Y: 5, Z: 0}
      - {X: 5, Y: 0, Z: 0}
      - {X: 0, Y: 0, Z: 0}
```

**边界条件对照表:**

| Surface Type | Location | Outside Boundary Condition | Sun/Wind |
|-------------|----------|---------------------------|----------|
| Floor | 首层 | Ground | NoSun/NoWind |
| Floor | 非首层 | Surface | NoSun/NoWind |
| Roof | 顶层 | Outdoors | SunExposed/WindExposed |
| Ceiling | 非顶层 | Surface | NoSun/NoWind |
| Wall | 外墙 | Outdoors | SunExposed/WindExposed |
| Wall | 内墙 | Surface | NoSun/NoWind |

---

### FenestrationSurface:Detailed Section (门窗部分)

```yaml
FenestrationSurface:Detailed:
  - Name: Zone_West_Window_North_1   # 必需，唯一名称
    Surface Type: Window             # Window/Door/GlassDoor
    Construction Name: Window_Const  # 必须引用已定义的 Construction
    Building Surface Name: Zone_West_Wall_North  # 父墙体表面名称
    Outside Boundary Condition Object: null
    View Factor to Ground: autocalculate
    Frame and Divider Name: null     # 窗框 (可选)
    Multiplier: 1
    Number of Vertices: autocalculate
    Vertices:                        # 窗户顶点
      - {X: 4, Y: 5, Z: 2}
      - {X: 4, Y: 5, Z: 1}
      - {X: 1, Y: 5, Z: 1}
      - {X: 1, Y: 5, Z: 2}
```

---

### HVAC Section (暖通部分)

```yaml
HVAC:
  HVACTemplate:Zone:IdealLoadsAirSystem:
    - Zone Name: Zone_West           # 必须引用已定义的 Zone
      Template Thermostat Name: Ideal Loads Thermostat  # 引用恒温器
      System Availability Schedule Name: Always On      # 引用 Schedule

  HVACTemplate:Thermostat:
    - Name: Ideal Loads Thermostat
      Heating Setpoint Schedule Name: Heating_Setpoint_Schedule  # 引用 Schedule
      Cooling Setpoint Schedule Name: Cooling_Setpoint_Schedule  # 引用 Schedule
```

---

## Important Validation Rules (重要验证规则)

### 表面顶点规则
- 每个表面必须有4个顶点（矩形表面）
- 从外部观察时，顶点必须逆时针排列
- 顶点之间的最小距离: 1e-10
- 热区内的所有表面必须形成封闭体积

### 内墙规则
- 连接两个热区的内墙必须有配对的表面
- 使用 `Outside Boundary Condition: Surface`
- 必须指定 `Outside Boundary Condition Object` 为配对表面名称

### 引用完整性
- 所有 `Construction Name` 必须引用已定义的 Construction
- 所有 `Zone Name` 必须引用已定义的 Zone
- 所有 `Schedule` 引用必须指向已定义的 Schedule
- 所有 `Material` 在 Layers 中的引用必须存在于 Material 部分

---

## Reference Files (参考文件)

- `docs/yaml-schema-reference.md` - 完整字段参考
- `docs/complexity-presets.md` - 复杂度级别配置
- `docs/geometry-rules.md` - 顶点计算公式
- `docs/error-handling.md` - 错误模式和修复
- `examples/` - 各复杂度级别的工作示例
