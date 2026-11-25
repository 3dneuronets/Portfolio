"""
Contributors: diogoleonaisouza@gmail.com, fernandodasilvaborges@gmail.com
"""
"""
batch.py

Batch simulation for H01 L23 model using NetPyNE
"""

from netpyne.batch import Batch
from netpyne import specs
import numpy as np

# -------------------------------------------------------------------
# Parameters
# -------------------------------------------------------------------

def custom():

    params = specs.ODict()

    # ---------------------------------------------------------------
    # Parameters to explore
    # ---------------------------------------------------------------

    params['GLOBALSEED'] = [1234]#,4321,9342,1243,3214,4123,4412,2231,5542,6674]

    b = Batch(
        params=params,
        netParamsFile='netParams.py',
        cfgFile='cfg.py',
    )
    return b


# -------------------------------------------------------------------
# Run configuration
# -------------------------------------------------------------------

def setRunCfg(b, run_type='mpi_bulletin'):

    if run_type == 'mpi_bulletin':

        b.runCfg = {'type': 'mpi_bulletin', 
            'script': 'init.py', 
            'skipCustom': '_data.pkl'
        }
        
    elif run_type == 'mpi_direct':

        b.runCfg = {
            'type': 'mpi_direct',
            'cores': 20,
            'script': 'init.py',
            'mpiCommand': 'mpiexec',
        }


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

if __name__ == '__main__':

    b = custom()
    # b.batchLabel = 'BASELINE_CoreNEURON_2'
    b.batchLabel = 'v1_batch1'
    b.saveFolder = '../data/' + b.batchLabel
    b.method = 'grid'

    setRunCfg(b,'mpi_direct') # Change to mpi_direct if you wanna use CPU and to mpi_bulletin if GPU is enabled in cfg

    b.run()

    