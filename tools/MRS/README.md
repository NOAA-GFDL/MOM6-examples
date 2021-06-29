# Scripts used in testing MOM6 commits against the various regression repositories

- **These scripts are not for general consumption** - they are mostly written in gnu-make so good luck figuring out how they work! :)
  But seriously, they are written for a particular sequence of tests, assuming a specific setup on a specific platform, and so they really will not be much use to you.
  We are not supporting these scripts for other platforms - sorry.

## Contents

- Makefile.build : rules to build executables
- Makefile.clone : rules to clone coupled components (must be inside GFDL firewall)
- Makefile.run   : rules to run experiments

## Build executables

From top-level of MOM6-examples (use CONFIGS if invoking from elsewhere):
```bash
make -f tools/MRS/Makefile.build repro_gnu -s -j
make -f tools/MRS/Makefile.build repro_intel -s -j
make -f tools/MRS/Makefile.build repro_pgi -s -j
make -f tools/MRS/Makefile.build debug_gnu -s -j
make -f tools/MRS/Makefile.build debug_intel -s -j
make -f tools/MRS/Makefile.build debug_pgi -s -j
make -f tools/MRS/Makefile.build openmp_gnu -s -j
make -f tools/MRS/Makefile.build openmp_intel -s -j
make -f tools/MRS/Makefile.build openmp_pgi -s -j
make -f tools/MRS/Makefile.build static_gnu -s -j
make -f tools/MRS/Makefile.build static_intel -s -j
make -f tools/MRS/Makefile.build static_pgi -s -j
```

Specific targets can be built, e.g.
```
make build/gnu/debug/dynamic_symmetric/ice_ocean_SIS2/MOM6
```

## Run model

From top-level of MOM6-examples (use CONFIGS if invoking from elsewhere):
```bash
make -f tools/MRS/Makefile.run gnu_all -s -j
make -f tools/MRS/Makefile.run intel_all -s -j
make -f tools/MRS/Makefile.run pgi_all -s -j
```
will yield a clean MOM6-examples (uses the correct layouts). `MEMORY=dynamic_symmetric` by default.

Test the non-symmetric executables with:
```bash
make -f tools/MRS/Makefile.run gnu_all MEMORY=dynamic_nonsymmetric -s -j
make -f tools/MRS/Makefile.run intel_all MEMORY=dynamic_nonsymmetric -s -j
make -f tools/MRS/Makefile.run pgi_all MEMORY=dynamic_nonsymmetric -s -j
```
which will produce different `MOM_parameter_doc.layout` files in MOM6-examples but with the right answers.

To use static executables:
```bash
make -f tools/MRS/Makefile.run gnu_static_ocean_only MEMORY=static -s -j
make -f tools/MRS/Makefile.run intel_static_ocean_only MEMORY=static -s -j
make -f tools/MRS/Makefile.run pgi_static_ocean_only MEMORY=static -s -j
```

Test with alternative PE counts:
```bash
make -f tools/MRS/Makefile.run gnu_all -s -j LAYOUT=alt
make -f tools/MRS/Makefile.run intel_all -s -j LAYOUT=alt
make -f tools/MRS/Makefile.run pgi_all -s -j LAYOUT=alt
```

Test with debug executables:
```bash
make -f tools/MRS/Makefile.run gnu_all -s -j MODE=debug
make -f tools/MRS/Makefile.run intel_all -s -j MODE=debug
make -f tools/MRS/Makefile.run pgi_all -s -j MODE=debug
```

## Copy results to regressions/
```bash
make -f tools/MRS/Makefile.sync -s -k
```
will sync the newly generated ocean/seaice.stats files and report their status.

```bash
make -f tools/MRS/Makefile.sync -s -k gnu
```
will sync only the gnu stats files.


## Test restarts

```bash
make -f tools/MRS/Makefile.restart gnu_ocean_only -s -j RESTART_STAGE=02
make -f tools/MRS/Makefile.restart gnu_ocean_only -s -j RESTART_STAGE=01
make -f tools/MRS/Makefile.restart gnu_ocean_only -s -j RESTART_STAGE=12
make -f tools/MRS/Makefile.restart gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=02
make -f tools/MRS/Makefile.restart gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=01
make -f tools/MRS/Makefile.restart gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=12
make -f tools/MRS/Makefile.restart restart_gnu_ocean_only -s -j
make -f tools/MRS/Makefile.restart restart_gnu_ice_ocean_SIS2 -s -j
make -f tools/MRS/Makefile.restart gnu_ocean_only gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=02
make -f tools/MRS/Makefile.restart gnu_ocean_only gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=01
make -f tools/MRS/Makefile.restart gnu_ocean_only gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=12
make -f tools/MRS/Makefile.restart restart_gnu_ocean_only restart_gnu_ice_ocean_SIS2 -s -j
```
Last commands alone is sufficient but seems more susceptible to lustre file systems flakiness.

## Build coverage report

```bash
make -f MRS/Makefile.coverage gnu_ocean_only -s MEMORY=dynamic_symmetric
make -f MRS/Makefile.coverage gnu_ice_ocean_SIS2 -s
make -f MRS/Makefile.coverage coverage
```

```bash
make -f tools/MRS/Makefile.run gnu_all MEMORY=dynamic_symmetric -s -j && make -f tools/MRS/Makefile.run intel_all -s -j && make -f tools/MRS/Makefile.run all MEMORY=dynamic_symmetric -s -j
```
