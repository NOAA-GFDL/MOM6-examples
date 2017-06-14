
from __future__ import print_function

import pytest
import os
import f90nml
from experiment import Experiment

def modify_input_nml(exp, set_ensemble_size=True, set_short_runtime=False):

    if set_ensemble_size or set_short_runtime:
        nml = f90nml.read(os.path.join(exp.path, 'input.nml'))
        if set_ensemble_size:
            nml['ensemble_nml'] = f90nml.namelist.Namelist()
            nml['ensemble_nml']['ensemble_size'] = 2
        if set_short_runtime:
            nml['coupler_nml']['days'] = 1

        f90nml.write(nml, os.path.join(exp.path, 'input.nml'), force=True)


class TestDomainTransform:
    """
    This test runs two test MOM6/SIS2 cases side-by-side. These cases are the
    same except that one of them has it's domain transformed. The
    transformation can be either a transpose or a rotation. As they run the
    side-by-side test cases compare key fields. If these fields differ in any
    way then the test fails.

    The test catches a large class of indexing errors, as well any differences
    in code between the i and j directions.
    """

    def test_baltic_transpose(self):
        """
        Test that the Baltic tests case gives identical results with a
        transposed domain.
        """

        exp = Experiment('ice_ocean_SIS2/Baltic')

        # Setup MOM_input for the test.
        exp.set_mom_input_option('DEBUG', 'True')
        exp.set_mom_input_option('TRANSFORM_TEST', 'True')
        exp.set_mom_input_option('DIFFUSE_ML_TO_INTERIOR', 'False')
        exp.set_mom_input_option('RESTORE_SALINITY', 'False')
        exp.set_sis_input_option('TRANSFORM_TEST', 'True')

        modify_input_nml(exp, set_short_runtime=True)

        # FIXME: empty the diag_table.

        # Run test.
        ret = exp.force_run()
        assert ret == 0


    @pytest.mark.skip
    def test_baltic_rotate90(self):
        pass

    @pytest.mark.skip
    def test_baltic_rotate180(self):
        pass

    @pytest.mark.skip
    def test_double_gyre_transpose(self):
        """
        Test that the double gyre case gives identical results with a
        transposed domain.
        """

        exp = Experiment('ocean_only/double_gyre')

        # Setup MOM_input for the test.
        exp.set_mom_input_option('DEBUG', 'True')
        exp.set_mom_input_option('TRANSFORM_TEST', 'True')
        exp.set_mom_input_option('DAYMAX', '1.0')
        exp.set_mom_input_option('NIGLOBAL', '40')

        modify_input_nml(exp)

        # Run test.
        ret = exp.force_run()
        assert ret == 0


    @pytest.mark.skip
    def test_double_gyre_rotate90(self):
        pass

    @pytest.mark.skip
    def test_double_gyre_rotate180(self):
        pass

