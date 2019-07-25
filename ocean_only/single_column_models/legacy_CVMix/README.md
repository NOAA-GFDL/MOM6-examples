# CVmix single column tests

## Summary of configurations

### mech_only

ICs: Linear thermal stratification, constant salinity, u* 

Forcing: constant u*, zero wind stress, zero buoyancy forcing

### wind_only

ICs: Linear thermal stratification, constant salinity, u* 

Forcing: zero background u*, constant wind stress, zero buoyancy forcing

### skin_warming_wind

ICs: Isothermal stratification, constant salinity, u* 

Forcing: zero background u*, constant wind stress, constant warming surface heat flux

## Directory structure

```
.
|-- common_BML          - Reused files for all bulk mixed-layer tests
|-- common_EPBL         - Reused files for all energetic planetary boundary layer tests
|-- common_KPP          - Reused files for all CVmix KPP tests
|-- cooling_only
|   |-- BML
|   |-- EPBL
|   `-- KPP
|-- mech_only
|   |-- BML
|   |-- EPBL
|   `-- KPP
|-- skin_warming_wind
|   |-- BML
|   |-- EPBL
|   `-- KPP
`-- wind_only
    |-- BML
    |-- EPBL
    `-- KPP
```
