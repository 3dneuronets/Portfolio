import sys
import pickle
import numpy as np
from metrics import *

# read variables of file
# v = str(sys.argv[1])
# batch = sys.argv[2]
# batch_number = 'batch'+str(batch.zfill(4))
# subbatch = sys.argv[3]
# subbatch_number = '0_'+str(subbatch)
# delta = int(sys.argv[4])
# file = f'../data/v{v}_{batch_number}/v{v}_{batch_number}_{subbatch_number}'

file = f'../data/v0_batch1/v0_batch1'
delta = 2


print('\n~~ Pre processing ')
print(f'~ Read file: {file}')
with open(file+'_data.pkl', 'rb') as f:
    data = pickle.load(f)

# n_neighbors = data['simConfig']['n_neighbors']
# cellNumber = data['simConfig']['cellNumber']
# r = n_neighbors / cellNumber
# data['r'] = r
# print(f'Cell number: {cellNumber} \t n_neighbors: {n_neighbors} \t r: {r}')
t_data, v_data = get_numpy(data)

ti_sample = 0
# tf_sample = 51001

# data['ti_sample'] = ti_sample
# data['tf_sample'] = tf_sample

v_sample = v_data[:, ti_sample:] 
t_sample = t_data[ti_sample:]


print('~ Computing phase')
result_phase = phase_of_v(t_sample, v_sample, return_peaks=True)
t_phase, phases, peaksmat, t_peaks, id_first_spk, id_last_spk = result_phase
data['t_phase'] = t_phase
data['phases'] = phases
data['peaksmat'] = peaksmat
data['t_peaks'] = t_peaks
data['id_first_spk'] = id_first_spk
data['id_last_spk'] = id_last_spk

print('~ Computing GOP')
gop = np.zeros(phases.shape[1])
for i, spatial_phase in enumerate(phases.T):
    gop[i] = kuramoto_param_global_order(spatial_phase)
data['GOP'] = gop

get_size(file+'_data.pkl')
print(f'~ Dump pickle file: {file}\n')
with open(file+'_data.pkl', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
get_size(file+'_data.pkl')

