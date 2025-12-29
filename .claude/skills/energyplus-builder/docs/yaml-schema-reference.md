# YAML Schema Reference (YAML 格式参考)

本文档提供 EnergyPlus 建筑配置中所有 YAML 字段的完整参考。

## Required Sections Overview (必需部分概览)

| Section | Required | Description | 描述 |
|---------|----------|-------------|------|
| SimulationControl | Yes | Simulation parameters | 模拟控制参数 |
| Building | Yes | Building metadata | 建筑元数据 |
| Timestep | Yes | Time step configuration | 时间步长配置 |
| Site:Location | Yes | Geographic location | 地理位置 |
| RunPeriod | Yes | Simulation period | 模拟周期 |
| Material | Yes | Building materials | 建筑材料 |
| Construction | Yes | Material assemblies | 材料组合 |
| GlobalGeometryRules | Yes | Coordinate system | 坐标系统 |
| Zone | Yes | Thermal zones | 热区 |
| BuildingSurface:Detailed | Yes | Building surfaces | 建筑表面 |
| FenestrationSurface:Detailed | No | Windows/doors | 门窗 |
| Schedule | Yes | Time schedules | 时间表 |
| HVAC | Yes | HVAC systems | 暖通系统 |
| Output:* | Yes | Output settings | 输出设置 |

---

## SimulationControl (模拟控制)

```yaml
SimulationControl:
    Do Zone Sizing Calculation: No          # Yes/No - 是否进行热区尺寸计算
    Do System Sizing Calculation: No        # Yes/No - 是否进行系统尺寸计算
    Do Plant Sizing Calculation: No         # Yes/No - 是否进行设备尺寸计算
    Run Simulation for Sizing Periods: No   # Yes/No - 是否为设计日运行模拟
    Run Simulation for Weather File Run Periods: Yes  # Yes/No - 是否为气象文件运行模拟
    Do HVAC Sizing Simulation for Sizing Periods: Yes # Yes/No (可选)
    Maximum Number of HVAC Sizing Simulation Passes: 1 # int (可选)
```

---

## Building (建筑)

```yaml
Building:
    Name: string                    # 必需，非空，建筑名称
    North Axis: float               # 0-359.99，默认 0，北轴角度
    Terrain: string                 # Suburbs/City/Country/Ocean/Urban，地形类型
    Loads Convergence Tolerance Value: float    # >0，默认 0.04，负荷收敛容差
    Temperature Convergence Tolerance Value: float  # >0，默认 0.4，温度收敛容差
    Solar Distribution: string      # 太阳辐射分布选项 (见下)
    Maximum Number of Warmup Days: int   # >=0，默认 25，最大预热天数
    Minimum Number of Warmup Days: int   # >=0，默认 0，最小预热天数
```

**Solar Distribution Options (太阳分布选项):**
- `FullExterior` - 仅外表面
- `MinimalShadowing` - 最小阴影
- `FullInteriorAndExterior` - 内外表面完整计算 (推荐)
- `FullExteriorWithReflections` - 外表面含反射
- `FullInteriorAndExteriorWithReflections` - 内外表面含反射

---

## Timestep (时间步长)

```yaml
Timestep:
    Number of Timesteps per Hour: int  # >=1，默认 4，每小时时间步数
```

**常用值:** 4 (15分钟), 6 (10分钟), 12 (5分钟)

---

## Site:Location (场地位置)

```yaml
Site:Location:
    Name: string         # 必需，非空，位置名称
    Latitude: float      # -90 到 90，纬度 (度)
    Longitude: float     # -180 到 180，经度 (度)
    Time Zone: float     # -12 到 14，时区 (小时)
    Elevation: float     # 海拔高度 (米)
```

---

## RunPeriod (运行周期)

```yaml
RunPeriod:
    Name: string                    # 必需，运行周期名称
    Begin Month: int                # 1-12，起始月
    Begin Day of Month: int         # 1-31，起始日
    Begin Year: int                 # 可选，起始年
    End Month: int                  # 1-12，结束月
    End Day of Month: int           # 1-31，结束日
    End Year: int                   # 可选，结束年
    Day of Week for Start Day: string  # 起始日星期
    Use Weather File Holidays and Special Days: Yes/No
    Use Weather File Daylight Saving Period: Yes/No
    Apply Weekend Holiday Rule: Yes/No
    Use Weather File Rain Indicators: Yes/No
    Use Weather File Snow Indicators: Yes/No
```

**Day of Week 选项:** `Sunday`, `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`

---

## Material (材料)

支持四种材料类型：

### 1. Standard Material (标准材料)
```yaml
Material:
  - Name: string           # 必需，唯一名称
    Type: Standard         # 类型标识
    Roughness: string      # 粗糙度: VeryRough/Rough/MediumRough/MediumSmooth/Smooth/VerySmooth
    Thickness: float       # >0，厚度 (m)
    Conductivity: float    # >0，导热系数 (W/m-K)
    Density: float         # >0，密度 (kg/m³)
    Specific_Heat: float   # >0，比热容 (J/kg-K)
```

### 2. NoMass Material (无质量材料)
```yaml
Material:
  - Name: string
    Type: NoMass
    Roughness: string          # 同上
    Thermal_Resistance: float  # >0，热阻 (m²-K/W)
```

### 3. AirGap Material (空气层材料)
```yaml
Material:
  - Name: string
    Type: AirGap
    Thermal_Resistance: float  # >0，热阻 (m²-K/W)
```

### 4. Glazing Material (玻璃材料)
```yaml
Material:
  - Name: string
    Type: Glazing
    U-Factor: float                      # >0，传热系数 (W/m²-K)
    Solar_Heat_Gain_Coefficient: float   # >0，太阳得热系数 (SHGC)
    Visible_Transmittance: float         # 0-1，可见光透射率 (可选)
```

---

## Construction (构造)

```yaml
Construction:
  - Name: string      # 必需，唯一名称
    Layers:           # 材料层列表，从外到内排列
      - MaterialName1
      - MaterialName2
```

**重要:** `Layers` 中引用的所有材料必须在 `Material` 部分定义。

---

## GlobalGeometryRules (全局几何规则)

```yaml
GlobalGeometryRules:
    Starting Vertex Position: string  # UpperLeftCorner/LowerLeftCorner/UpperRightCorner/LowerRightCorner
    Vertex Entry Direction: string    # Counterclockwise/Clockwise (推荐 Counterclockwise)
    Coordinate System: string         # World/Relative (推荐 World)
```

---

## Zone (热区)

```yaml
Zone:
  - Name: string                       # 必需，唯一名称
    Direction of Relative North: null  # 0-359.99 或 null，相对北向
    X Origin: float                    # X原点坐标 (m)
    Y Origin: float                    # Y原点坐标 (m)
    Z Origin: float                    # Z原点坐标 (m)，表示楼层高度
    Type: int                          # >=0，默认 1，热区类型
    Multiplier: int                    # >=1，默认 1，乘数
    Ceiling Height: float/string       # >0 或 "autocalculate"，层高
    Volume: float/string               # >0 或 "autocalculate"，体积
    Floor Area: float/string           # >0 或 "autocalculate"，地面积
```

---

## BuildingSurface:Detailed (建筑表面详细)

```yaml
BuildingSurface:Detailed:
  - Name: string                           # 必需，唯一名称
    Surface Type: string                   # Floor/Wall/Ceiling/Roof
    Construction Name: string              # 必须引用已定义的 Construction
    Zone Name: string                      # 必须引用已定义的 Zone
    Space Name: null                       # 可选
    Outside Boundary Condition: string     # Ground/Outdoors/Surface/Adiabatic
    Outside Boundary Condition Object: string/null  # 如果 OBC=Surface 则必需
    Sun Exposure: string                   # SunExposed/NoSun
    Wind Exposure: string                  # WindExposed/NoWind
    View Factor to Ground: float/string    # 0-1 或 "autocalculate"
    Vertices:                              # 顶点列表 (3个或更多)
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
```

### Surface Type 与边界条件对照表

| Surface Type | 位置 | Outside Boundary Condition | Sun Exposure | Wind Exposure |
|-------------|------|---------------------------|--------------|---------------|
| Floor | 首层 (地面) | Ground | NoSun | NoWind |
| Floor | 非首层 | Surface | NoSun | NoWind |
| Roof | 顶层 | Outdoors | SunExposed | WindExposed |
| Ceiling | 非顶层 | Surface | NoSun | NoWind |
| Wall | 外墙 | Outdoors | SunExposed | WindExposed |
| Wall | 内墙 | Surface | NoSun | NoWind |

---

## FenestrationSurface:Detailed (门窗表面详细)

```yaml
FenestrationSurface:Detailed:
  - Name: string                           # 必需，唯一名称
    Surface Type: string                   # Window/Door/GlassDoor
    Construction Name: string              # 必须引用已定义的 Construction
    Building Surface Name: string          # 父墙体表面名称
    Outside Boundary Condition Object: null
    View Factor to Ground: float/string    # 0-1 或 "autocalculate"
    Frame and Divider Name: null           # 窗框分隔名称 (可选)
    Multiplier: int                        # >=1，乘数
    Number of Vertices: int/string         # >=3 或 "autocalculate"
    Vertices:
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
      - {X: float, Y: float, Z: float}
```

---

## Schedule (时间表) ⚠️ 重要更新

Schedule 部分采用嵌套结构，包含两个子部分。这是格式最复杂的部分，需要特别注意。

### 完整结构概览

```yaml
Schedule:
  ScheduleTypeLimits:     # 时间表类型限制定义 (列表)
    - ...
  Schedule:Compact:       # 紧凑格式时间表 (列表)
    - ...
```

### ScheduleTypeLimits (时间表类型限制)

定义时间表数值的约束条件。

```yaml
Schedule:
  ScheduleTypeLimits:
    # 开关类型 - 用于可用性调度
    - Name: On/Off                    # 必需，唯一名称
      Lower Limit Value: 0            # 下限值 (数值或省略)
      Upper Limit Value: 1            # 上限值 (数值或省略)
      Numeric Type: DISCRETE          # DISCRETE 或 CONTINUOUS
      Unit Type: Dimensionless        # 单位类型
      
    # 温度类型 - 用于设定点调度
    - Name: Temperature
      Numeric Type: CONTINUOUS        # 连续型数值
      Unit Type: Temperature          # 温度单位
      # Lower/Upper Limit Value 可省略表示无限制
```

**字段说明:**

| 字段 | 必需 | 类型 | 说明 |
|-----|------|-----|------|
| Name | 是 | string | 唯一标识符 |
| Lower Limit Value | 否 | float/省略 | 数值下限 |
| Upper Limit Value | 否 | float/省略 | 数值上限 |
| Numeric Type | 是 | string | `DISCRETE` (离散) 或 `CONTINUOUS` (连续) |
| Unit Type | 是 | string | 见下方单位类型列表 |

**Unit Type 选项:**
- `Dimensionless` - 无量纲
- `Temperature` - 温度
- `Power` - 功率
- `Availability` - 可用性
- `Percent` - 百分比

---

### Schedule:Compact (紧凑格式时间表)

定义具体的时间-值调度。采用嵌套的 Through → Days → Times 结构。

```yaml
Schedule:
  Schedule:Compact:
    - Name: Always On                     # 必需，唯一名称
      Schedule Type Limits Name: On/Off   # 必须引用已定义的 ScheduleTypeLimits
      Data:                               # 数据部分 (列表)
        - Through: "12/31"                # 日期范围截止点 (最后必须是 12/31)
          Days:                           # 天类型定义 (列表)
          - For: "AllDays"                # 适用的天类型
            Times:                        # 时间-值对 (列表)
            - Until:
                Time: "24:00"             # 时间点 (最后必须是 24:00)
                Value: 1                  # 对应值
```

### 完整 Schedule 示例

```yaml
Schedule:
  ScheduleTypeLimits:
    - Name: On/Off
      Lower Limit Value: 0
      Upper Limit Value: 1
      Numeric Type: DISCRETE
      Unit Type: Dimensionless
      
    - Name: Temperature
      Numeric Type: CONTINUOUS
      Unit Type: Temperature

  Schedule:Compact:
    # 常开调度 - 用于系统可用性
    - Name: Always On
      Schedule Type Limits Name: On/Off
      Data:
        - Through: "12/31"
          Days:
          - For: "AllDays"
            Times:
            - Until:
                Time: "24:00"
                Value: 1

    # 供暖设定点调度
    - Name: Heating_Setpoint_Schedule
      Schedule Type Limits Name: Temperature
      Data:
        - Through: "12/31"
          Days:
          - For: "AllDays"
            Times:
            - Until:
                Time: "24:00"
                Value: 20

    # 制冷设定点调度
    - Name: Cooling_Setpoint_Schedule
      Schedule Type Limits Name: Temperature
      Data:
        - Through: "12/31"
          Days:
          - For: "AllDays"
            Times:
            - Until:
                Time: "24:00"
                Value: 26
```

### 复杂调度示例 (办公建筑)

```yaml
Schedule:
  Schedule:Compact:
    - Name: Office_Occupancy
      Schedule Type Limits Name: On/Off
      Data:
        - Through: "12/31"
          Days:
          - For: "Weekdays"           # 工作日
            Times:
            - Until:
                Time: "08:00"
                Value: 0              # 8:00前无人
            - Until:
                Time: "18:00"
                Value: 1              # 8:00-18:00有人
            - Until:
                Time: "24:00"
                Value: 0              # 18:00后无人
          - For: "Weekends"           # 周末
            Times:
            - Until:
                Time: "24:00"
                Value: 0              # 全天无人
```

### Schedule 数据结构层级

```
Schedule
├── ScheduleTypeLimits (列表)
│   └── [每个类型限制项]
│       ├── Name (string)
│       ├── Lower Limit Value (float, 可选)
│       ├── Upper Limit Value (float, 可选)
│       ├── Numeric Type (string)
│       └── Unit Type (string)
│
└── Schedule:Compact (列表)
    └── [每个调度项]
        ├── Name (string)
        ├── Schedule Type Limits Name (string, 引用)
        └── Data (列表)
            └── [每个日期段]
                ├── Through (string, "MM/DD")
                └── Days (列表)
                    └── [每个天类型]
                        ├── For (string, 天类型)
                        └── Times (列表)
                            └── [每个时间点]
                                └── Until
                                    ├── Time (string, "HH:MM")
                                    └── Value (number)
```

### Schedule 验证规则 ⚠️

1. **日期范围要求:**
   - 最后一个 `Through` 必须是 `"12/31"`
   - `Through` 值格式为 `"MM/DD"`

2. **时间要求:**
   - 每个 `Days` 块的最后一个 `Time` 必须是 `"24:00"`
   - `Time` 格式为 `"HH:MM"`

3. **引用完整性:**
   - `Schedule Type Limits Name` 必须引用已定义的 `ScheduleTypeLimits`
   - HVAC 等部分引用的 Schedule 名称必须存在

4. **有效的 Day Types:**
   - `AllDays` - 所有天
   - `Weekdays` - 工作日
   - `Weekends` - 周末
   - `Holidays` - 节假日
   - `SummerDesignDay` - 夏季设计日
   - `WinterDesignDay` - 冬季设计日
   - `Sunday`, `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`

---

## HVAC (暖通空调)

### HVACTemplate:Zone:IdealLoadsAirSystem
```yaml
HVAC:
  HVACTemplate:Zone:IdealLoadsAirSystem:
    - Zone Name: string                          # 必须引用已定义的 Zone
      Template Thermostat Name: string           # 必须引用已定义的 Thermostat
      System Availability Schedule Name: string  # 必须引用已定义的 Schedule
```

### HVACTemplate:Thermostat
```yaml
HVAC:
  HVACTemplate:Thermostat:
    - Name: string                              # 必需，唯一名称
      Heating Setpoint Schedule Name: string    # 必须引用已定义的 Schedule
      Cooling Setpoint Schedule Name: string    # 必须引用已定义的 Schedule
```

### 完整 HVAC 示例

```yaml
HVAC:
  HVACTemplate:Zone:IdealLoadsAirSystem:
    - Zone Name: Zone_West
      Template Thermostat Name: Ideal Loads Thermostat
      System Availability Schedule Name: Always On
      
    - Zone Name: Zone_East 
      Template Thermostat Name: Ideal Loads Thermostat
      System Availability Schedule Name: Always On
      
  HVACTemplate:Thermostat:
    - Name: Ideal Loads Thermostat
      Heating Setpoint Schedule Name: Heating_Setpoint_Schedule
      Cooling Setpoint Schedule Name: Cooling_Setpoint_Schedule
```

---

## Output Settings (输出设置)

```yaml
Output:VariableDictionary:
    Key Field: string   # regular/IDF

Output:Diagnostics:
    Key 1: string       # DisplayExtraWarnings 等

Output:Table:SummaryReports:
    Report 1 Name: string  # AllSummary 等

OutputControl:Table:Style:
    Column Separator: string  # HTML/Comma/Tab 等
    Unit Conversion: string   # None/JtoKWH 等 (可选)

Output:Variable:
  - Key Value: string         # "*" 或具体热区名
    Variable Name: string     # EnergyPlus 变量名
    Reporting Frequency: string  # Timestep/Hourly/Daily/Monthly/Annual
```

### 常用输出变量

```yaml
Output:Variable:
  - Key Value: "*"
    Variable Name: Zone Mean Air Temperature
    Reporting Frequency: Hourly
    
  - Key Value: "*"
    Variable Name: Surface Inside Face Temperature
    Reporting Frequency: Hourly
    
  - Key Value: "*"
    Variable Name: Zone Air System Sensible Cooling Energy
    Reporting Frequency: Hourly
    
  - Key Value: "*"
    Variable Name: Zone Air System Sensible Heating Energy
    Reporting Frequency: Hourly
```

---

## 引用完整性检查清单

在生成 YAML 之前，确保：

1. ✅ 所有 `Construction.Layers` 中的材料名称存在于 `Material` 部分
2. ✅ 所有 `BuildingSurface.Construction Name` 引用存在于 `Construction` 部分
3. ✅ 所有 `BuildingSurface.Zone Name` 引用存在于 `Zone` 部分
4. ✅ 所有 `FenestrationSurface.Construction Name` 引用存在于 `Construction` 部分
5. ✅ 所有 `FenestrationSurface.Building Surface Name` 引用存在于 `BuildingSurface` 部分
6. ✅ 所有 `Schedule:Compact.Schedule Type Limits Name` 引用存在于 `ScheduleTypeLimits` 部分
7. ✅ 所有 `HVAC` 中的 Zone/Schedule/Thermostat 引用都存在
8. ✅ 配对的内墙表面 (`Outside Boundary Condition: Surface`) 相互引用
