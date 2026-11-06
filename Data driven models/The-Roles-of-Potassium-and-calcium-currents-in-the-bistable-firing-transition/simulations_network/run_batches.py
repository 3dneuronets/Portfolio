"""
run_batches.py

Script python to run n-th batches 

params: 
    - python3 batch.py version batch_number list_Gex list_Iinj

Contributors: conrad.bittencourt@gmail.com, fernandodasilvaborges@gmail.com
"""

import os
import numpy as np

# coupling of elements
gex = np.round(np.arange(0.001,1.2,0.1) * 1e-3, 4)
# external current
i_ext = np.round(np.linspace(83, 134, 12) * 1e-2, 3)
currents = np.array_split(i_ext, 4)

batch = 1
v = 1

for g in gex:
    for conn in currents:
        # os.system(f'python3 batch.py {v} {batch} {g:.6f} ' + f'{conn}')
        print(f'python3 batch.py {v} {batch} {g:.4f} ' + f'{conn}')
        batch+=1




