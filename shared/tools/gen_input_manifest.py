#!/usr/bin/env python3
import argparse
import os
import shutil
import sys

from parse_mom_input import parse_mom6_param

# Use the local version of f90nml
tools_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(tools_path, 'f90nml'))
import f90nml

parser = argparse.ArgumentParser()
parser.add_argument('expt', help='Path to experiment')
args = parser.parse_args()

expt_path = args.expt

# Verify output
if not os.path.isdir(os.path.abspath(expt_path)):
    sys.exit('Error: path "{}" not found.'.format(expt_path))

if not os.path.isfile(os.path.join(expt_path, 'input.nml')):
    sys.exit('Error: no "input.nml" in "{}"'.format(expt_path))


# All FMS files must have `input.nml`.
manifest = ['input.nml']

# The following are standard FMS inputs.
FMS_tables = [
    'diag_table',
    'data_table',
    'field_table',
]

manifest += [
    f for f in FMS_tables if os.path.isfile(os.path.join(expt_path, f))
]


# Input directories are optional
if os.path.isdir(os.path.join(expt_path, 'INPUT')):
    manifest += ['INPUT']

# NOTE: MOM6 may define separate directories for restarts.  This is not yet
# handled.


# Parse parameter inputs
input_nml = f90nml.read(os.path.join(expt_path, 'input.nml'))

for grp in ('MOM_input_nml', 'SIS_input_nml', 'ice_ocean_driver_nml'):
    params = input_nml.get(grp, {}).get('parameter_filename', [])
    if isinstance(params, str):
        params = [params]
    manifest += params


# TODO: Constructing the complete manifest for a general run is a difficult
#   task, if not impossible.  But this is sufficient for now.
param_path = os.path.join(expt_path, 'MOM_parameter_doc.all')
with open(param_path) as param_file:
    params = parse_mom6_param(param_file)

coord_config = params['COORD_CONFIG']
if coord_config == 'file':
    inputdir = params['INPUTDIR']

    if inputdir == '.':
        coord_file = params['COORD_FILE']
        coord_path = os.path.join(expt_path, coord_file)

        if os.path.isfile(coord_path):
            manifest += [coord_file]


# Output results in a shell-friendly format.
print(' '.join(manifest))
