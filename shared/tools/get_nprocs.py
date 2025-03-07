#!/usr/bin/env python
import os
import sys

try:
    import psutil
    max_cpus = psutil.cpu_count(logical=False)
except ImportError:
    max_cpus = None

from parse_mom_input import parse_mom6_param

# Use the local version of f90nml
tools_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(tools_path, 'f90nml'))
import f90nml


# TODO: argparse
if len(sys.argv) != 2:
    sys.exit('Error: Experiment path missing.')

expt_path = sys.argv[1]
if not os.path.isdir(os.path.abspath(expt_path)):
    sys.exit('Error: path "{}" not found.'.format(expt_path))

if not os.path.isfile(os.path.join(expt_path, 'input.nml')):
    sys.exit('Error: no "input.nml" in "{}"'.format(expt_path))

# Bad flag detection
limit_cpus = max_cpus and any(arg == '-f' for arg in sys.argv)


# Parse parameter inputs
input_nml = f90nml.read(os.path.join(expt_path, 'input.nml'))

npes = 0

# First check if this is a coupled model
if 'coupler_nml' in input_nml:
    coupler_nml = input_nml['coupler_nml']

    atmos_npes = coupler_nml.get('atmos_npes', 0)
    ocean_npes = coupler_nml.get('ocean_npes', 0)

    if atmos_npes + ocean_npes > 0:
        concurrent = coupler_nml['concurrent']

        if concurrent:
            npes = atmos_npes + ocean_npes
        else:
            # Is this what I want??
            npes = max(atmos_npes, ocean_npes)

        # TODO:

# If coupler_nml is zero or unavailable, then check MOM_paramer_doc.layout.
if npes == 0:
    param_path = os.path.join(expt_path, 'MOM_parameter_doc.layout')
    with open(param_path) as param_file:
        params = parse_mom6_param(param_file)

    niproc = int(params['NIPROC'])
    njproc = int(params['NJPROC'])
    masktable = params.get('MASKTABLE')

    nmask = 0
    if masktable:
        # TODO: Use params('INPUTDIR')?
        mask_path = os.path.join(expt_path, 'INPUT', masktable)

        if os.path.isfile(mask_path):
            with open(mask_path) as mask_file:
                nmask = int(mask_file.readline())

    npes = niproc * njproc - nmask


# Limit CPUs to platform if requested
# NOTE: This will change `MOM_parameter_doc.layout`.
if limit_cpus:
    npes = min(npes, max_cpus)

# Always use at least one CPU
npes = max(npes, 1)

print(npes)
