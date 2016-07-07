
from __future__ import print_function

import sys
import os
import subprocess as sp
import shlex

_build_fms_script = """
../../../../mkmf/bin/list_paths ../../../../src/FMS &&
../../../../mkmf/bin/mkmf -t ../../../../mkmf/templates/{site}-{compiler}.mk -p libfms.a -c "-Duse_libMPI -Duse_netCDF -DSPMD" path_names &&
source ../../../../mkmf/env/{site}-{compiler}.env && make NETCDF=3 {build}=1 libfms.a -j
"""

_build_ocean_script = """
pwd &&
../../../../../mkmf/bin/list_paths ./ ../../../../../src/MOM6/{{config_src/{memory_type},config_src/solo_driver,src/{{*,*/*}}}}/
../../../../../mkmf/bin/mkmf -t ../../../../../mkmf/templates/{site}-{compiler}.mk -o '-I../../../shared/{build}' -p 'MOM6 -L../../../shared/{build} -lfms' -c "-Duse_libMPI -Duse_netCDF -DSPMD" path_names &&
source ../../../../../mkmf/env/{site}-{compiler}.env && make NETCDF=3 {build}=1 MOM6 -j
"""

_build_ocean_ice_script = """
pwd &&
../../../../../mkmf/bin/list_paths ./ ../../../../../src/MOM6/config_src/{{{memory_type},coupled_driver}} ../../../../../src/MOM6/src/{{*,*/*}}/ ../../../../../src/{{atmos_null,coupler,land_null,SIS2,ice_ocean_extras,icebergs,FMS/coupler,FMS/include}} &&
../../../../../mkmf/bin/mkmf -t ../../../../../mkmf/templates/{site}-{compiler}.mk -o '-I../../../shared/{build}' -p 'MOM6 -L../../../shared/{build} -lfms' -c '-Duse_libMPI -Duse_netCDF -DSPMD -DUSE_LOG_DIAG_FIELD_INFO' path_names &&
source ../../../../../mkmf/env/{site}-{compiler}.env && make NETCDF=3 {build}=1 MOM6 -j
"""

def mkdir_p(path):
    """Create a new directory; ignore if it already exists."""
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def get_shared_build_dir(mom_dir, compiler, build):
    return os.path.join(mom_dir, 'build', compiler, 'shared', build)


def get_model_build_dir(mom_dir, compiler, model_name, build, memory_type):
    return os.path.join(mom_dir, 'build', compiler, model_name, build,
                         memory_type)

class Model:

    def __init__(self, name, mom_dir):
        self.name = name
        self.mom_dir = mom_dir
        self.site = 'raijin'

    def build(self, compiler, build, memory_type):
        sret, shared_dir = self.build_shared(compiler, build)
        mret, model_dir = self.build_model(compiler, build, memory_type)
        exe = os.path.join(model_dir, 'MOM6') 

        return sret + mret, exe

    def build_shared(self, compiler, build):
        saved_path = os.getcwd()
        ret = 0

        # Build FMS
        shared_dir = get_shared_build_dir(self.mom_dir, compiler, build)
        mkdir_p(shared_dir)
        os.chdir(shared_dir)
        command = _build_fms_script.format(site=self.site, build=build,
                                           compiler=compiler)
        try:
            output = sp.check_output(command, stderr=sp.STDOUT, shell=True)
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        with open(os.path.join(shared_dir, 'build.out'), 'w') as f:
            f.write(output)

        return ret, shared_dir


    def build_model(self, compiler='gnu', build='REPRO', memory_type='dynamic'):
        """
        Build this model.
        """
        saved_path = os.getcwd()
        ret = 0

        # Build either ocean_only or ice and ocean.

        model_dir = get_model_build_dir(self.mom_dir, compiler, self.name,
                                        build, memory_type)
        mkdir_p(model_dir)
        os.chdir(model_dir)
        if self.name == 'ocean_only':
            command = _build_ocean_script.format(site=self.site, build=build,
                                                 compiler=compiler,
                                                 memory_type=memory_type)
        elif self.name == 'ice_ocean_SIS2':
            command = _build_ocean_ice_script.format(site=self.site, build=build,
                                                     compiler=compiler,
                                                     memory_type=memory_type)
        else:
            print('Unsupported model type', file=sys.stderr)
            assert False
        try:
            output = sp.check_output(command, stderr=sp.STDOUT, shell=True)
        except sp.CalledProcessError as e:
            ret = e.returncode
            output = e.output
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        with open(os.path.join(model_dir, 'build.out'), 'w') as f:
            f.write(output)

        return ret, model_dir

