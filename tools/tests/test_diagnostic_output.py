
from __future__ import print_function

import sys
import os
from netCDF4 import Dataset
import numpy as np
import hashlib
import pytest

DO_CHECKSUM_TEST = False

@pytest.mark.usefixtures('prepare_to_test')
class TestDiagnosticOutput:

    def test_coverage(self, exp):
        """
        Test that all available diagnostics can be dumped.
        """
        # Check that none of the experiments unfinished diags have been
        # implemented, if so the unifinished_diags list should be updated.
        assert(not any([os.path.exists(d.output) for d in exp.get_unfinished_diags()]))

        # Check that diags that should have been written out are.
        assert(len(exp.get_available_diags()) > 0)
        for d in exp.get_available_diags():
            if not os.path.exists(d.output):
                print('Error: diagnostic output {} not found.'.format(d.output),
                        file=sys.stderr)
        assert(all([os.path.exists(d.output) for d in exp.get_available_diags()]))

    def test_valid(self, exp):
        """
        Check that that all output diagnostics are valid.

        Validity checks:
            - contain the expected variable
            - the variable contains data
            - that data doesn't contain NaNs.
        """
        for d in exp.get_available_diags():
            with Dataset(d.output) as f:
                assert(d.name in f.variables.keys())
                data = f.variables[d.name][:].copy()
                assert(len(data) > 0)

                if hasattr(data, 'mask'):
                    assert(not data.mask.all())
                assert(not np.isnan(np.sum(data)))

    @pytest.mark.skip(reason="This test is high maintenance. Also see DO_CHECKSUM_TEST.")
    def test_checksums(self, exp):
        """
        Test that checksums of diagnostic output are the same
        as a baseline.
        """

        checksum_file = os.path.join(exp.path, 'diag_checksums.txt')
        tmp_file = os.path.join(exp.path, 'tmp_diag_checksums.txt')
        new_checksums = ''
        for d in exp.get_available_diags():
            # hash the diagnostic data in the output file
            with Dataset(d.output) as f:
                checksum = hashlib.sha1(f.variables[d.name][:].data.tobytes()).hexdigest()

            # add the text data
            new_checksums += '{}:{}\n'.format(os.path.basename(d.output),
                                              checksum)

        # Read in the baseline and check against calculated.
        with open(checksum_file) as f:
            baseline = f.read()

        if baseline != new_checksums and DO_CHECKSUM_TEST:
            with open(tmp_file, 'w') as f:
                f.write(new_checksums)
            print('Error: diagnostic checksums do not match.',
                  file=sys.stderr)
            print('Compare {} and {}'.format(checksum_file, tmp_file),
                  file=sys.stderr)
            print('If the difference is expected then' \
                  ' update {}'.format(checksum_file), file=sys.stderr)
            assert(baseline == new_checksums)
