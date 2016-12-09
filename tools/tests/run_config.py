
import socket
import os

def get_exec_prefix(model, exp_name, variation):
    """
    Return a prefix needed to execute the given experiment.

    model is the model configuration, e.g. ice_ocean_SIS2 or ocean_only
    exp_name is the experiment name, e.g. Baltic or global_ALE
    variation is the a variation on the experiment, e.g. z, layer. 
    """

    exec_prefix = 'mpirun -n 2'

    pbs_o_host = os.getenv('PBS_O_HOST')
    if pbs_o_host is not None and 'gaea' in pbs_o_host:
        exec_prefix = 'aprun -n 1'

    return exec_prefix
