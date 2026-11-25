
"""
netParams.py

... model using NetPyNE

Contributors: conrad.bittencourt@gmail.com, fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import os
import numpy as np

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = 1.0 # Scale factor for number of cells
netParams.sizeX = 100.0 # x-dimension (horizontal length) size in um
netParams.sizeY = 100.0 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 100.0 # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume
   
netParams.propVelocity = 300.0    # propagation velocity (um/ms)
netParams.probLengthConst = 10.0 # length constant for conn probability (um)


#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------
for cellName in cfg.allcells:
    cellRule = netParams.importCellParams(label=cellName + '_rule', somaAtOrigin=False,
        conds={'cellType': cellName, 'cellModel': 'HH_simple'},
        fileName='cells/PospischilEtAl2008/cellwrapper_Pospischil2008.py',
        cellName='loadCell',
        cellArgs={'template': cellName},
        cellInstance = True,
        importSynMechs=True
        )

    # observation:
    # - when import template cells the label of 'soma' is 'soma_0'.
    print(netParams.cellParams[cellName + '_rule']['secs']['soma_0'])

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------

# for ith-pop create pop with ith-cell of allcells 

for i, pop in enumerate(cfg.allpops):
    netParams.popParams[pop] = {
        'cellType': cfg.allcells[i],
        'cellModel': 'HH_simple',
        'numCells': cfg.cellNumber
    }

#------------------------------------------------------------------------------
# Current inputs (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:
     for key in [k for k in dir(cfg) if k.startswith('IClamp')]:
        params = getattr(cfg, key, None)
        [pop,sec,loc,start,dur,amp] = [params[s] for s in ['pop','sec','loc','start','dur','amp']]

        #cfg.analysis['plotTraces']['include'].append((pop,0))  # record that pop
        # add stim source
        netParams.stimSourceParams[key] = {'type': 'IClamp', 'delay': start, 'dur': dur, 'amp': amp}
        # connect stim source to target
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop},
            'sec': f'{sec}_0', # target 'soma_0'
            'loc': loc}


#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------

# netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 15.0, 'tau2': 150.0, 'e': 0.0}
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0.0}
#ESynMech    = ['AMPA', 'NMDA']
#------------------------------------------------------------------------------
# Connectivity rules
#------------------------------------------------------------------------------

netParams.connParams['EE'] = { 
    'preConds': {'pop': cfg.allpops}, 
    'postConds': {'pop': cfg.allpops},
    'synMech': 'AMPA', # ESynMech,
    'probability': 0.1, 
    'weight': cfg.gex, # 'delay': 'defaultDelay+dist_3D/propVelocity', 'synsPerConn': int(synperconnNumber[pre][post]+0.5)
    }    