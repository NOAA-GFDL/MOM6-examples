
import os

import pytest
from dump_all_diagnostics import dump_diags
from experiment import create_experiments, exp_id_from_path

def pytest_addoption(parser):
    parser.addoption('--exps', default=None,
                     help="""comma-separated no spaces list of experiments to
                             pass to test functions. Also you must use the '='
                             sign otherwise py.test gets confused, e.g:
                             $ py.test --exps=ice_ocean_SIS2/Baltic/,ocean_only/benchmark""")
    parser.addoption('--full', action='store_true', default=False,
                     help="""Run on all experiments/test cases. By default
                             tests are run on a 'fast' subset of experiments.
                             Note that this overrides the --exps option.""")
    parser.addoption('--platform', default='raijin',
                     help="""Which machine we're on. This determines how
                             the model is built. Currently supported options
                             are 'raijin' and 'ubuntu'.""")


def pytest_generate_tests(metafunc):
    """
    Parameterize tests. Presently handles those that have 'exp' as an argument.
    """
    experiment_dict = create_experiments(metafunc.config.option.platform)

    if 'exp' in metafunc.fixturenames:
        if metafunc.config.option.full:
            # Run tests on all experiments.
            exps = experiment_dict.values()
        elif metafunc.config.option.exps is not None:
            # Only run on the given experiments.
            exps = []
            for p in metafunc.config.option.exps.split(','):
                assert(os.path.exists(p))
                id = exp_id_from_path(os.path.abspath(p))
                exps.append(experiment_dict[id])
        else:
            # Default is to run on a fast subset of the experiments.
            exps = [experiment_dict['ice_ocean_SIS2/Baltic']]

        metafunc.parametrize('exp', exps, indirect=True)

@pytest.fixture
def exp(request):
    """
    Called before each test, use this to dump all the experiment data.
    """
    exp = request.param

    # Run the experiment to get latest code changes. This will do nothing if
    # the experiment has already been run.
    exp.run()
    # Dump all available diagnostics, if they haven't been already.
    if not exp.has_dumped_diags:
        # Before dumping we delete old ones if they exist.
        diags = exp.get_available_diags()
        for d in diags:
            try:
                os.remove(d.output)
            except OSError:
                pass

        dump_diags(exp, diags)
        exp.has_dumped_diags = True
    return exp

def restore_after_test():
    """
    Restore experiment state after running a test.

    - The diag_table files needs to be switched back (?)
    """
    pass

@pytest.fixture(scope='module')
def prepare_to_test():
    """
    Called once for a test module.

    - Make a backup of the diag_table, to be restored later. (?)
    """
    pass
