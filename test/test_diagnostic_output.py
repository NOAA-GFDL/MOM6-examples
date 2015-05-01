
from __future__ import print_function

import os
import re
import sys
import numpy as np
import hashlib
from scipy.io import netcdf as nc
from experiment import Experiment

from nose import with_setup

def get_expected_diags(exp):
    """
    Parse available_diags.000001 and SIS.available_diags files to get a list of
    all possible diags for this experiment.
    """

    mom_av_file = os.path.join(exp.path, 'available_diags.000000')
    sis_av_file = os.path.join(exp.path, 'SIS.available_diags')
    assert(os.path.exists(mom_av_file))
    assert(os.path.exists(sis_av_file))

    expected_diags = []
    for fname in [mom_av_file, sis_av_file]:
        with open(fname) as f:
            # Seach or strings like: "ocean_model", "N2_u"  [Unused] and
            # pull out the model name and variable name.
            expected_diags.extend(re.findall('^\"(\w+)\", \"(\w+)\".*$',
                                             f.read(), re.MULTILINE))
    return expected_diags

def dump_diags(exp, diags):
    """
    Create a new diag_table based on the given diags in experiment 'exp', run
    the experiment so that all diagnostics are written out.
    """

    # Create a new diag_table that dumps all diagnostics into individual
    # files. This is a trick to get the highest frequency output for each
    # diagnostic. By default if only a single file is used, when '0' is set
    # as the frequency, the diag manager will choose the minimum frequency
    # and dump all diagnostics with that. This will result in the slower
    # diagnostics being filled up with missing values, which is not what we
    # want.
    with open(os.path.join(exp.path, 'diag_table'), 'w') as f:
        print('test_diags_coverage', file=f)
        print('1 1 1 0 0 0', file=f)
        for m, d in diags:
            print('"{}_{}", 0, "seconds", 1, "seconds", "time"'.format(m, d), file=f)
        for m, d in diags:
            print('"{}", "{}", "{}", "{}_{}", "all",' \
                  '.false., "none", 2'.format(m, d, d, m, d), file=f)

    # Run model again. An output file for each diagnostic will be written.
    assert(exp.run())

def diag_filenames(exp, diags):
    """
    Take a list of diagnostics and return a list of tuples, first element of
    tuple is the full path to the file containing the diagnostic.
    """

    with_filenames = []
    for m, d in diags:
        fname = os.path.join(exp.path, '00010101.{}_{}.nc'.format(m, d))
        with_filenames.append((fname, d))

    return with_filenames


class TestDiagnosticOutput:

    exp = ('ice_ocean_SIS2', 'Baltic')

    def __init__(self):

        self.exp = Experiment(*TestDiagnosticOutput.exp)

        # These are diagnostics which have been registered but have not been
        # implemented yet, so no post_data called. This list should to be
        # updated as the diags are finished.
        unfinished_diags = [('ocean_model', 'uml_restrat'),
                            ('ocean_model', 'vml_restrat'),
                            ('ocean_model', 'created_H'),
                            ('ocean_model', 'seaice_melt'),
                            ('ocean_model', 'fsitherm'),
                            ('ocean_model', 'total_seaice_melt'),
                            ('ocean_model', 'heat_restore'),
                            ('ocean_model', 'total_heat_restore'),
                            ('ice_model', 'Cor_ui'),
                            ('ice_model', 'Cor_vi'),
                            ('ice_model', 'OBI'),
                            ('ice_model', 'RDG_OPEN'),
                            ('ice_model', 'RDG_RATE'),
                            ('ice_model', 'RDG_VOSH'),
                            ('ice_model', 'STRAIN_ANGLE'),
                            ('ice_model', 'SW_DIF'),
                            ('ice_model', 'SW_DIR'),
                            ('ice_model', 'TA')]
        self.unfinished_diags = diag_filenames(self.exp, unfinished_diags)
        self.expected_diags = diag_filenames(self.exp,
                                             get_expected_diags(self.exp))
        self.available_diags = list(set(self.expected_diags) - \
                                     set(self.unfinished_diags))


    @classmethod
    def setUpClass(cls):
        """
        Called once for this class. Sets up the external state used by all
        tests.
        """

        exp = Experiment(*cls.exp)
        # Build and run the model to begin to pick up recent code changes.
        assert(exp.run())

        diags = get_expected_diags(exp)
        # Delete any existing diag output
        for f, _ in diag_filenames(exp, diags):
            try:
                os.remove(f)
            except:
                pass

        # Update the diag table and run again, this should dump all available
        # diagnostics.
        dump_diags(exp, diags)

    def test_diags_coverage(self):
        """
        Test that all available diagnostics are created.
        """

        # Check that none of the unfinished diags have been implemented, if so
        # the unifinished_diags list above should be updated.
        assert(not any([os.path.exists(f) for f, _ in self.unfinished_diags]))

        # Check that diags that should have been written out are.
        assert(len(self.available_diags) > 0)
        assert(all([os.path.exists(f) for f, _ in self.available_diags]))

    def test_diags_valid(self):
        """
        Check that that all output files contain the expected variable, that
        the variable contains data, and that that data doesn't contain NaNs.
        """

        for fname, diag in self.available_diags:
            with nc.netcdf_file(fname) as f:
                assert(diag in f.variables.keys())
                data = f.variables[diag][:].copy()
                assert(len(data) > 0)

                if hasattr(data, 'mask'):
                    assert(not data.mask.all())
                assert(not np.isnan(np.sum(data)))


    def make_diag_checksums(self):
        """
        Return a string of checksums for all diagnostic output files.

        The files need to be in netCDF3 format, netCDF4 is not bit reproducible.
        """

        s = ''
        for fname, _ in sorted(self.available_diags):
            with open(fname, 'rb') as in_f:
                checksum = hashlib.md5(in_f.read()).hexdigest()
                s += '{}:{}\n'.format(os.path.basename(fname), checksum)

        return s

    def test_diag_checksums(self):
        """
        Test that checksums of diagnostic output are the same as a baseline.
        """

        checksum_file = os.path.join(self.exp.path, 'diag_checksums.txt')
        tmp_file = os.path.join(self.exp.path, 'tmp_diag_checksums.txt')
        new_checksums = self.make_diag_checksums()

        # Read in the baseline and check against calculated.
        with open(checksum_file) as f:
            baseline = f.read()
        if baseline != new_checksums:
            with open(tmp_file, 'w') as f:
                f.write(new_checksums)
            print('Error: diagnostic checksums do not match.',
                  file=sys.stderr)
            print('Compare {} and {}'.format(checksum_file, tmp_file),
                  file=sys.stderr)
            print('If the difference is expected then' \
                  ' update {}'.format(checksum_file), file=sys.stderr)
            assert(False)
