# This is the FCML (Free Convection Mixed Layer) experiment from Van Roekel et al. (2018)

## Forcing parameters

Sensible Heat Flux = -75 W/m2

SW Heat Flux (peak) = 0 W/m2

Evaporation = 0 mm/day

Wind stress = 0 N/m2

Rotation: f = 1e-4 s-1

## Initial profile

Temperature profile: T(Z) = 20 [degC]  for Z > -25 m

		     T(Z) = 20 [degC] + 0.01 [degC/m] * (Z+25) [m]   for Z < -25m

Salinity profile:    S(Z) = 35 [g/kg] for Z > -25 m

		     S(Z) = 35 [g/kg] - 0.03 [g/kg/m] (Z+25) [m] for -25 m > Z >-35 m

		     S(Z) = 35.3 [g/kg] for Z < -35 m