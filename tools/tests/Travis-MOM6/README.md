## Travis-CI testing script for MOM6 repository

- Invoked for MOM6 Travis-CI configuration https://github.com/NOAA-GFDL/MOM6/blob/dev/master/.travis.yml .
- This script lives with MOM6-examples since it runs some of the examples and thus
  needs to be consistent with MOM6-examples at all times.

### Environment

- The environment is determined/controlled by the .travis.yml file in the MOM6 repository.
  - Assumes the following packages were installed on top of the "c" language Travis docker image:
    - tcsh
    - pkg-config
    - gfortran
    - netcdf-bin
    - libnetcdf-dev
    - openmpi-bin
    - libopenmpi-dev

## What happens

1. Travis clones the MOM6 repository and checks out a specific commit (e.g. a pull request).
2. MOM6/.travis.yml clones MOM6-examples that contains the scripts in this directory.
   - This is not a recursive clone. Only these scripts, FMS and mkmf are required.
3. MOM6/.travis.yml then invokes each of these scripts from the level above MOM6.
   - build_fms.sh (builds libfms.a)
   - before_script.sh (makes adjustments to configs so they fit within Travis VM)
   - build_ocean_only.sh (builds MOM6 in non-symmetric memeory mode)
   - build_symmetric_ocean_only.sh (builds MOM6 in symmetric memeory mode)
   - run_tests.sh (run a select few tests with 1-core and 2/4-core combinatinos of
     symmetric and non-symmetric mode)
