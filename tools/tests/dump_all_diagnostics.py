#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
from experiment import Experiment

"""
This script is used to run an experiment/test case and dump all available
diagnostics. This can be useful for testing or to get a feel for the range of
model outputs.
"""

def dump_diags(exp, diags):
    """
    Run the model dumping the given diagnostics into individual files.
    """

    # Create a new diag_table that puts diagnostics into individual files. This
    # is a trick to get the highest frequency output for each diagnostic.
    #
    # By default if only a single file is used, when '0' is set as the
    # frequency, the diag manager will choose the minimum frequency and dump
    # all diagnostics with that. This will result in the slower diagnostics
    # being filled up with missing values which is not desirable.

    with open(os.path.join(exp.path, 'diag_table'), 'w') as f:
        print('All {} diags'.format(exp.name), file=f)
        print('1 1 1 0 0 0', file=f)
        for d in diags:
            print('"{}_{}", 0, "seconds", 1, "seconds",' \
                  '"time"'.format(d.model, d.name), file=f)
        for d in diags:
            m = d.model
            n = d.name
            print('"{}", "{}", "{}", "{}_{}", "all",' \
                  '.false., "none", 2'.format(m, n, n, m, n), file=f)
    return exp.force_run()

def main():

    description = "Run an experiment and dump all it's available diagnostics."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('experiment_path',
                        help='path to experiment to run.')

    args = parser.parse_args()
    exp = Experiment(path=os.path.abspath(args.experiment_path))
    diags = exp.get_available_diags()
    return dump_diags(exp, diags)

if __name__ == '__main__':
    sys.exit(main())
