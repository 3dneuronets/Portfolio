import pickle
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.font_manager
import os
import sys

def plot_params():
    plt.rc('text', usetex=True)
    plt.rc('font', size=13)
    plt.rc('xtick', labelsize=11)
    plt.rc('ytick', labelsize=11)
    plt.rc('axes', labelsize=14)
    plt.rc('legend', fontsize=8)
    plt.rc('lines', linewidth=1.0)
    plt.rcParams["axes.formatter.limits"] = (-3, 4)
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
plot_params()

def plotRaster(t_phase_smp, t_peaks):
    fig, (ax0, ax1) = plt.subplots(2,1, figsize=(8,4), gridspec_kw = {'height_ratios':[4, 1]})
    fig.set_tight_layout(20)

    # ax.set_title('$g_{syn}='+f'{gex}$S/cm²', fontsize=14)
    ax0.spines['right'].set_visible(False)
    ax0.spines['top'].set_visible(False)
    ax0.set_title('Raster Plot of Network',pad=20)
    ax0.set_ylabel('$i$ neuron')
    ax0.set_ylim(0, len(t_peaks))
    ax0.set_xlim(1000,3000)
    ax0.eventplot(t_peaks, color='purple')

    ax1.plot(data['simData']['t'][10000:], data['simData']['V_soma']['cell_10'][10000:], color='red')
    ax1.plot(data['simData']['t'][10000:], data['simData']['V_soma']['cell_50'][10000:], color='green')
    ax1.plot(data['simData']['t'][10000:], data['simData']['V_soma']['cell_60'][10000:], color='blue')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.set_xlim(1000,3000)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('V (mV)')

    plt.savefig(file+f'_PlotRaster_{gex}_{amp}.png', dpi=600, bbox_inches='tight')
    # plt.show()

# v = str(sys.argv[1])
# batch = sys.argv[2]
# batch_number = 'batch'+str(batch.zfill(4))
# subbatch = sys.argv[3]
# subbatch_number = '0_'+str(subbatch)

# file = f'../data/v{v}_{batch_number}/v{v}_{batch_number}_{subbatch_number}'
file = f'../data/v0_batch1/v0_batch1'

print('~~ Plot Raster')
print(f'Reading: "{file}"')

with open(file+'_data.pkl', 'rb') as f:
    data = pickle.load(f)
    
gex = data['simConfig']['gex']
amp = data['simConfig']['IClamp0']['amp']
# popRates = data['simData']['popRates']['pop_sPY']
t_phase = data['t_phase']
t_peaks = data['t_peaks']

plotRaster(t_phase, t_peaks)

print('\n~~')
