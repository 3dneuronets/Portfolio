
"""
.py

High-level specifications for S1 network model using NetPyNE

Contributors: fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import pickle, json
import os
import numpy as np
import pandas as pd

netParams = specs.NetParams()   # object of class NetParams to store the network parameters


try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

#------------------------------------------------------------------------------

for ii in range(4,8):

    with open('../data/v8_batch' + str(ii) + '/v8_batch' + str(ii) + '_0_0_data.pkl', 'rb') as fileObj: spikesData = pickle.load(fileObj)

    spkid = spikesData['simData']['spkid']
    spkt = spikesData['simData']['spkt']


    #------------------------------------------------------------------------------
    spkTimes = {}
    popID = {}
    N = 0
    for metype in cfg.cellNumber.keys():      
        for i in range(N,N+cfg.cellNumber[metype]):
            spkTimes[metype+'_'+str(i)] = []
        
        popID[metype] = N
        N += cfg.cellNumber[metype]

        print(metype,cfg.cellNumber[metype],'N =',N,', Number of spikes =',np.size(spkt),', FR =',np.size(spkt)/(12.0*N))

    for mtype in cfg.thalamicpops:
        metype = mtype
        cfg.popLabelEl[mtype] = []
        cfg.popLabelEl[mtype].append(metype)

    for mtype in cfg.popNumber.keys():
        for metype in cfg.popLabelEl[mtype]:  
            for i in range(np.size(spkt)):
                if spkt[i] > 6000 and spkid[i] >= popID[metype] and spkid[i] < popID[metype]+cfg.cellNumber[metype]:
                    spkTimes[metype+'_'+str(int(spkid[i]))].append(spkt[i] - 6000)

    #------------------------------------------------------------------------------
    cellsTags = []
    for i,metype in enumerate(spikesData['net']['cells']):
        if i < N:
            cellsTags2 = {}
            for tp in ['cellType', 'xnorm', 'ynorm', 'znorm', 'x', 'y', 'z']:
                cellsTags2[tp] = metype.tags[tp]            
            cellsTags.append(cellsTags2)

        print(cellsTags2, i, 'N =',N)

    #------------------------------------------------------------------------------
    # Save data to pkl file
    with open('../data/spkTimes_v8_batch' + str(ii) + '_6s.pkl', 'wb') as f:
        pickle.dump({'spkTimes': spkTimes, 'cellsTags': cellsTags}, f)
