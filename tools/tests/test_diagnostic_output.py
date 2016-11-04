
from __future__ import print_function

import sys
import os
from netCDF4 import Dataset
import numpy as np
import hashlib
import pytest

from dump_all_diagnostics import dump_diags

DO_CHECKSUM_TEST = False

# FIXME: why are these different between the old and new z remapped diags.
# 1. The new z units for uh, vh are incorrect.
not_tested_z_diags = ['uh', 'vh', 'Kd_interface', 'Kd_itides', 'age']

def compare_rho_to_layer(coord_diags, layer_diags):

    layer_dict = {}
    for d in layer_diags:
        layer_dict[d.name] = d

    for da in coord_diags:
        db = layer_dict[da.name]

        fa = Dataset(da.output)
        fb = Dataset(db.output)
        va = fa.variables[da.name][:]
        vb = fb.variables[da.name][:]

        # Compare time axes.
        assert np.array_equal(fa.variables['time'][:], fb.variables['time'][:])

        # Compare the masks. Presently does not work for fields on interfaces.
        if not 'i:point' in fa.variables[da.name].cell_methods:
            assert np.array_equal(va.mask, vb.mask)

        if 'l:sum' in fa.variables[da.name].cell_methods:
            # This will include, for example, uh, vh, h
            assert np.allclose(np.sum(va, axis=1), np.sum(vb, axis=1), rtol=1e-2)

        fa.close()
        fb.close()


def compare_z_to_zold_diags(diagA, diagB):

    assert diagA.name == diagB.name

    fa = Dataset(diagA.output)
    fb = Dataset(diagB.output)

    # Don't expect the time resolution to be the same.
    small = fa
    big = fb
    if len(fa.variables['time']) > len(fb.variables['time']):
        small = fb
        big = fa

    vs = small.variables[diagA.name][:]
    ts = small.variables['time'][:]
    vb = big.variables[diagA.name][:]
    tb = big.variables['time'][:]

    # The smaller must be a subset of the larger.
    assert set(ts).issubset(set(tb))

    # Get indices where time points are the same.
    cmp_idxs = np.argwhere(np.in1d(tb, ts)).flatten()
    vb = vb[cmp_idxs, :]

    # Check that masks are identical
    # FIXME: this doesn't work. The new diags use a mask which a straight
    # extension of G%mask2d with no variation in the vertical, while the old
    # diags masks include bathymetry and ice shelf depth.
    # assert np.array_equal(vs.mask, vb.mask)

    # Take into account that masks can be different (see above). Make one mask
    # the combines the masked areas from both diags. Also sometimes the old
    # diags don't have a mask.
    if hasattr(vb, 'mask') or hasattr(vs, 'mask'):
        if not hasattr(vb, 'mask'):
            vb = np.ma.array(vb, mask=vs.mask)
        if not hasattr(vs, 'mask'):
            vs = np.ma.array(vs, mask=vb.mask)

        new_mask = np.ma.mask_or(vb.mask, vs.mask)
        vb.mask = new_mask
        vs.mask = new_mask

    # Min and max should be close
    assert np.isclose(np.max(vs), np.max(vb), rtol=1e-2)
    assert np.isclose(np.min(vs), np.min(vb), rtol=1e-2)

    # Sums should be close
    if diagA.name in ['u', 'v', 'uo', 'vo']:
        # FIXME: investigate why these are so different.
        assert np.isclose(np.sum(vb), np.sum(vs), rtol=5e-2)
    else:
        assert np.isclose(np.sum(vb), np.sum(vs), rtol=1e-2)

    fa.close()
    fb.close()

def dump_diags_for_coord(exp, coord):

    assert coord == 'z' or coord == 'rho' or coord == 'sigma'

    def is_rho(diag):
        return diag.model[-4:] == '_rho'
    def is_sigma(diag):
        return diag.model[-6:] == '_sigma'
    def is_z(diag):
        return diag.model[-2:] == '_z'
    def is_layer(diag):
        return diag.model == 'ocean_model'

    available_diags = exp.parse_available_diags(packed=False)

    if coord == 'rho':
        coord_diags = filter(is_rho, available_diags)
    if coord == 'z':
        coord_diags = filter(is_z, available_diags)
    if coord == 'sigma':
        coord_diags = filter(is_sigma, available_diags)
    layer_diags = filter(is_layer, available_diags)

    dump_diags(exp, coord_diags + layer_diags)

    return coord_diags, layer_diags


@pytest.mark.usefixtures('prepare_to_test')
class TestDiagnosticOutput:

    def test_coverage(self, exp):
        """
        Test that all available diagnostics can be dumped.
        """
        # Check that none of the experiments unfinished diags have been
        # implemented, if so the unifinished_diags list should be updated.
        for d in exp.get_unfinished_diags():
            if os.path.exists(d.output):
                with Dataset(d.output) as f:
                    assert not f.variables.has_key(d.name)

        # Check that diags that should have been written out are.
        assert(len(exp.get_diags()) > 0)
        for d in exp.get_diags():
            if not os.path.exists(d.output):
                print('Error: diagnostic output {} not found.'.format(d.output),
                        file=sys.stderr)
            assert os.path.exists(d.output)

            # Check that the output contains the expected variable
            with Dataset(d.output) as f:
                if not f.variables.has_key(d.name):
                    print('Error: diagnostic {} not found in {}.'.format(d.name, d.output),
                          file=sys.stderr)
                assert f.variables.has_key(d.name)


    def test_valid(self, exp):
        """
        Check that that all output diagnostics are valid.

        Validity checks:
            - contain the expected variable
            - the variable contains data
            - that data doesn't contain NaNs.
        """
        for d in exp.get_diags():
            with Dataset(d.output) as f:
                assert(d.name in f.variables.keys())
                data = f.variables[d.name][:].copy()
                assert(len(data) > 0)

                if hasattr(data, 'mask'):
                    assert(not data.mask.all())
                assert(not np.isnan(np.sum(data)))

    @pytest.mark.cmp_z_remap
    def test_cmp_z_zold_remapping(self, exp):
        """
        Compare the new z space diagnostics (calculated using ALE remapping) to
        the old z remapped diagnostics. We expect them to be very similar.
        """

        old_diags = []
        new_diags = []
        for d in exp.get_diags():
            # Get new and old z diags.
            if d.model[-5:] == '_zold' and d.name[-6:] != '_xyave':
                old_diags.append(d)
            elif d.model[-2:] == '_z':
                new_diags.append(d)

        assert len(old_diags) != 0
        assert len(new_diags) != 0

        old_diag_names = [d.name for d in old_diags]
        new_diag_names = [d.name for d in new_diags]
        assert set(old_diag_names).issubset(set(new_diag_names))

        for old in old_diags:
            for new in new_diags:
                if new.name == old.name and new.name not in not_tested_z_diags:
                    compare_z_to_zold_diags(old, new)
                    break

    @pytest.mark.rho_remap
    def test_rho_remapping(self, exp_diags_not_dumped):
        """
        Dump all rho diags into separate files.
        """

        rho_diags, layer_diags = dump_diags_for_coord(exp_diags_not_dumped, 'rho')

        compare_rho_to_layer(rho_diags, layer_diags)


    @pytest.mark.sigma_remap
    def test_sigma_remapping(self, exp_diags_not_dumped):
        """
        Dump all sigma diags into separate files.
        """

        sigma_diags, layer_diags = dump_diags_for_coord(exp_diags_not_dumped, 'sigma')

        # FIXME.
        # compare_sigma_to_layer(sigma_diags, layer_diags)


    @pytest.mark.z_remap
    def test_z_remapping(self, exp_diags_not_dumped):
        """
        Dump all z diags into separate files.
        """

        z_diags, layer_diags = dump_diags_for_coord(exp_diags_not_dumped, 'z')

        # FIXME.
        # compare_z_to_layer(z_diags, layer_diags)


    @pytest.mark.skip(reason="This test is high maintenance. Also see DO_CHECKSUM_TEST.")
    def test_checksums(self, exp):
        """
        Test that checksums of diagnostic output are the same
        as a baseline.
        """

        checksum_file = os.path.join(exp.path, 'diag_checksums.txt')
        tmp_file = os.path.join(exp.path, 'tmp_diag_checksums.txt')
        new_checksums = ''
        for d in exp.get_diags():
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
