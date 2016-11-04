#!/usr/bin/env python

from __future__ import print_function

import sys, os
import argparse
from experiment import Experiment
from experiment import exp_id_from_path

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
        for fname in list(set([d.filename for d in diags])):
            print('"{}", 0, "seconds", 1, "seconds",' \
                  '"time"'.format(fname), file=f)
        for d in diags:
            m = d.model
            n = d.name
            fname = d.filename
            print('"{}", "{}", "{}", "{}", "all",' \
                  '.false., "none", 2'.format(m, n, n, fname, n), file=f)
    return exp.force_run()

def main():

    description = "Run an experiment and dump all it's available diagnostics."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('exp_path',
                        help='path to experiment whose diagnostics will be dumped.')

    args = parser.parse_args()
    if not os.path.exists(args.exp_path):
      print('Experiment {} is not a valid path!'.format(args.exp_path),
             file=sys.stderr)
      parser.print_help()
      return 1

    exp_id = exp_id_from_path(args.exp_path)
    exp = Experiment(exp_id)
    diags = exp.get_available_diags()
    return dump_diags(exp, diags)

if __name__ == '__main__':
    sys.exit(main())
