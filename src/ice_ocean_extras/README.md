This directory contains source code needed to build an ice-ocean executable with either SIS1 or SIS2.
_This is an exception to the practice of not keeping source code in the MOM6-examples repository._
We are doing this since the code is not visible from outside of GFDL and we can avoid shipping
these files via ftp sites as we've done in the past.

It contains copies of source that are otherwise kept in the following repositories:
- diag_integral from sub-directory of http://gitlab.gfdl.noaa.gov/fms/atmos_param.git
- monin_obukhov from sub-directory of http://gitlab.gfdl.noaa.gov/fms/atmos_param.git
- ice_param from http://gitlab.gfdl.noaa.gov/fms/ice_param.git

When building coupled AOGCMs these source in this directory is not needed.
