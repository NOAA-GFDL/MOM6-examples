
from __future__ import print_function

import subprocess as sp
import os
import sys

class Experiment(object):

    def __init__(self, model, exp_name, platform='gnu'):
        """
        Python representation of an experiment / test case.
        """

        self.model = model
        self.exp_name = exp_name
        self.platform = platform
        # Path to experiment
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(self.script_path, '../', model, self.exp_name)

        # Path to exec.
        self.exec_path = os.path.join(self.script_path,
                                      '../build/{}/{}/repro/MOM6'.format(platform, model))
        assert(os.path.exists(self.exec_path))

    def force_build(self):
        """
        Do a clean build of the configuration.
        """
        raise NotImplementedError


    def build(self):
        """
        Build the configuration for this experiment.
        """
        raise NotImplementedError


    def run(self):
        """
        Run the given experiment.

        FIXME: should do a build when necessary.
        """

        print('Experiment: running {}'.format(self.exec_path))

        ret = 0
        saved_path = os.getcwd()

        os.chdir(self.path)
        try:
            output = sp.check_output([self.exec_path], stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        return (ret == 0)
