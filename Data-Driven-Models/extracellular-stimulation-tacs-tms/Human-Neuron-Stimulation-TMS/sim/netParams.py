# =============================================================================
# netParams.py  —  Network Parameters for L23Net NetPyNE Replica
# Yao et al. 2022 human Layer 2/3 cortical microcircuit
# =============================================================================
import os
import numpy as np
from netpyne import specs

from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

# L23 Human net
# #              L2/3   L4     L5
PYRmaxApics = [550   ,1550   ,1900]
uppers =      [-250  ,-1200 ,-1600]
lowers =      [-1200 ,-1580 ,-2300]

L25_human = 250 + 950 + 380 + 720 + 1000
Human_height = 3300.0

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = cfg.scale # Scale factor for number of cells
netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume
netParams.rotateCellsRandomly = True # rotate cell morphologies randomly along vertical axis (to avoid alignment artifacts)
   
cellModels = ['HH_full']

Ipops = ['HL23SST', 'HL23PV', 'HL23VIP']
Epops = ['HL23PYR']

layer = {'1':[0.0, 250.0], '23': [250.0,1200.0], '23soma': [-1500.0,-550.0], '4':[1200.0,1580.0], '5': [1580.0,2300.0], '6': [2300.0,3300.0]}  # normalized layer boundaries

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.defaultThreshold = -10.0 # spike threshold, 10 mV is NetCon default, lower it for all cells

# ---------------------------------------------------------------------------
# Paths (relative to NetPyNE_Replica_Yao/ working directory)
# ---------------------------------------------------------------------------
MODELS_DIR = 'models'

# =============================================================================
# SECTION 1: Cell Parameters (cellParams)
#
# Each cell type has a standalone wrapper HOC template (HL23XXX_Cell.hoc) that:
#   1. Loads the cell-specific SWC morphology (path hardcoded in the template)
#   2. Runs geom_nseg()
#   3. Applies the correct axon policy (delete_axon or delete_axon_BPO)
#   4. Calls biophys() — all channel insertions are done inside init()
#
# A single importCellParams call per cell type is sufficient.
# importCellParams instantiates the template, then scans h.allsec() to capture
# all section geometry + mechanisms into the cellParams secs dict.
# =============================================================================


for cell_name in cfg.allpops:
    wrapper_hoc   = os.path.join(MODELS_DIR, f'{cell_name}_Cell.hoc')
    template_name = cell_name + '_Cell'

    cellRule = netParams.importCellParams(
        label          = cell_name,
        fileName       = wrapper_hoc,
        cellName       = template_name,
        importSynMechs = False,
        somaAtOrigin   = True,
    )

    # Tag the rule so popParams can reference it by condition
    netParams.cellParams[cell_name]['conds'] = {
        'cellType':  cell_name,
        'cellModel': 'HH_full',
    }

    # Define named section lists for connParams compartment targeting.
    # These mirror the SWC section types used in the original HOC model.
    secs = netParams.cellParams[cell_name]['secs']
    apic_secs  = sorted([s for s in secs if s.startswith('apic')])
    dend_secs  = sorted([s for s in secs if s.startswith('dend')])
    soma_secs  = sorted([s for s in secs if s.startswith('soma')])
    axon_secs  = sorted([s for s in secs if s.startswith('axon') or s.startswith('myelin')])

    netParams.cellParams[cell_name]['secLists'] = {
        'all':     soma_secs + dend_secs + apic_secs + axon_secs,
        'spiny':   dend_secs + apic_secs,
        'somatic': soma_secs,
        'basal':   dend_secs,
        'apical':  apic_secs,
        'axonal':  axon_secs,
        # 'spiny' used internally; SYN_POS=0 is split into two rules
    }

# ----------------------------------------------------------------------------------------------------------------------- #
# Rotate to z as vertical
# ----------------------------------------------------------------------------------------------------------------------- #
if cfg.ROTATE_Y:

    rotate_x = {}
    rotate_y = {}
    rotate_z = {}
    rotate_x['HL23PYR'], rotate_x['HL23SST'], rotate_x['HL23PV'], rotate_x['HL23VIP'] = 1.57, 1.77, 1.26, -1.57
    rotate_y['HL23PYR'], rotate_y['HL23SST'], rotate_y['HL23PV'], rotate_y['HL23VIP'] = 2.62, 2.77, 2.57, 3.57
    rotate_z['HL23PYR'], rotate_z['HL23SST'], rotate_z['HL23PV'], rotate_z['HL23VIP'] = 0.0, 0.0, 0.0, 0.0


    for cellName in netParams.cellParams.keys():

        cellType = netParams.cellParams[cellName]['conds']['cellType']

        x = rotate_x[cellType]
        y = rotate_y[cellType]
        z = rotate_z[cellType]

        for sectName in netParams.cellParams[cellName]['secs'].keys():

            sectParams_new = netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d']
            sectParams = []

            theta = -x
            rotation_x = np.array([[1, 0, 0],
                                        [0, np.cos(theta), -np.sin(theta)],
                                        [0, np.sin(theta), np.cos(theta)]])
            
            # print(cellName,sectName,len(sectParams_new))
            # print(sectParams_new)       
            
            for i in range(len(sectParams_new)):
                x3d, y3d, z3d, L3d = sectParams_new[i]
                rel_pos = x3d, y3d, z3d

                # print(rel_pos)        
                rel_pos = np.dot(rel_pos, rotation_x)
                # print(rel_pos)
                pt3d = (rel_pos[0],rel_pos[1] , rel_pos[2], L3d)
                sectParams.append(pt3d)

            netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d'] = sectParams


            sectParams_new = netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d']
            sectParams = []

            phi = -y
            rotation_y = np.array([[np.cos(phi), 0, np.sin(phi)],
                                        [0, 1, 0],
                                        [-np.sin(phi), 0, np.cos(phi)]])
            
            for i in range(len(sectParams_new)):
                x3d, y3d, z3d, L3d = sectParams_new[i]
                rel_pos = x3d, y3d, z3d

                # print(rel_pos)        
                rel_pos = np.dot(rel_pos, rotation_y)
                # print(rel_pos)
                pt3d = (rel_pos[0],rel_pos[1] , rel_pos[2], L3d)
                sectParams.append(pt3d)

            netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d'] = sectParams


            sectParams_new = netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d']
            sectParams = []

            gamma = -z
            rotation_z = np.array([[np.cos(gamma), -np.sin(gamma), 0],
                                        [np.sin(gamma), np.cos(gamma), 0],
                                        [0, 0, 1]])
        
            for i in range(len(sectParams_new)):
                x3d, y3d, z3d, L3d = sectParams_new[i]
                rel_pos = x3d, y3d, z3d

                # print(rel_pos)        
                rel_pos = np.dot(rel_pos, rotation_z)
                # print(rel_pos)
                pt3d = (rel_pos[0],rel_pos[1] , rel_pos[2], L3d)
                sectParams.append(pt3d)

            netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d'] = sectParams

    # ----------------------------------------------------------------------------------------------------------------------- #
    # Rotate to Y as vertical axis
    # ----------------------------------------------------------------------------------------------------------------------- #

    rotate_x = {}
    rotate_y = {}
    rotate_z = {}
    rotate_x['HL23PYR'], rotate_x['HL23SST'], rotate_x['HL23PV'], rotate_x['HL23VIP'] = -1.5708, -1.5708, -1.5708, -1.5708
    rotate_y['HL23PYR'], rotate_y['HL23SST'], rotate_y['HL23PV'], rotate_y['HL23VIP'] = 0.0, 0.0, 0.0, 0.0
    rotate_z['HL23PYR'], rotate_z['HL23SST'], rotate_z['HL23PV'], rotate_z['HL23VIP'] = 0.0, 0.0, 0.0, 0.0


    for cellName in netParams.cellParams.keys():

        cellType = netParams.cellParams[cellName]['conds']['cellType']

        x = rotate_x[cellType]
        y = rotate_y[cellType]
        z = rotate_z[cellType]

        for sectName in netParams.cellParams[cellName]['secs'].keys():

            sectParams_new = netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d']
            sectParams = []

            theta = -x
            rotation_x = np.array([[1, 0, 0],
                                        [0, np.cos(theta), -np.sin(theta)],
                                        [0, np.sin(theta), np.cos(theta)]])
            
            # print(cellName,sectName,len(sectParams_new))
            # print(sectParams_new)       
            
            for i in range(len(sectParams_new)):
                x3d, y3d, z3d, L3d = sectParams_new[i]
                rel_pos = x3d, y3d, z3d

                # print(rel_pos)        
                rel_pos = np.dot(rel_pos, rotation_x)
                # print(rel_pos)
                pt3d = (rel_pos[0],rel_pos[1] , rel_pos[2], L3d)
                sectParams.append(pt3d)

            netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d'] = sectParams


            sectParams_new = netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d']
            sectParams = []

            phi = -y
            rotation_y = np.array([[np.cos(phi), 0, np.sin(phi)],
                                        [0, 1, 0],
                                        [-np.sin(phi), 0, np.cos(phi)]])
            
            for i in range(len(sectParams_new)):
                x3d, y3d, z3d, L3d = sectParams_new[i]
                rel_pos = x3d, y3d, z3d

                # print(rel_pos)        
                rel_pos = np.dot(rel_pos, rotation_y)
                # print(rel_pos)
                pt3d = (rel_pos[0],rel_pos[1] , rel_pos[2], L3d)
                sectParams.append(pt3d)

            netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d'] = sectParams


            sectParams_new = netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d']
            sectParams = []

            gamma = -z
            rotation_z = np.array([[np.cos(gamma), -np.sin(gamma), 0],
                                        [np.sin(gamma), np.cos(gamma), 0],
                                        [0, 0, 1]])
        
            for i in range(len(sectParams_new)):
                x3d, y3d, z3d, L3d = sectParams_new[i]
                rel_pos = x3d, y3d, z3d

                # print(rel_pos)        
                rel_pos = np.dot(rel_pos, rotation_z)
                # print(rel_pos)
                pt3d = (rel_pos[0],rel_pos[1] , rel_pos[2], L3d)
                sectParams.append(pt3d)

            netParams.cellParams[cellName]['secs'][sectName]['geom']['pt3d'] = sectParams


if cfg.Change_axon_names:
    #------------------------------------------------------------------------------
    # Change axon names
    #------------------------------------------------------------------------------
    # print and rename
    for cellName in netParams.cellParams.keys():
            
        if 'myelin_0' in netParams.cellParams[cellName]['secs'].keys():

            netParams.renameCellParamsSec(label=cellName, oldSec='myelin_0', newSec='axon_2')      
                
            for secname2 in netParams.cellParams[cellName]['secLists'].keys():
                if 'myelin_0' in netParams.cellParams[cellName]['secLists'][secname2]:
                    # print('old ->',cellName,secname2,netParams.cellParams[cellName]['secLists'][secname2][-1])
                    netParams.cellParams[cellName]['secLists'][secname2][-1] = 'axon_2'    
                    # print('new ->',cellName,secname2,netParams.cellParams[cellName]['secLists'][secname2][-1])


# =============================================================================
# SECTION 3: Population Parameters (popParams)
# L2/3 spatial geometry from original circuit.py:
#   upper = -250 µm, lower = -1200 µm  (z-axis, soma depth)
#   cylinder radius = 250 µm in x-y
# =============================================================================


L23_UPPER  = -250   # µm
L23_LOWER  = -1200  # µm
L23_RADIUS =  250   # µm
L23_UPPER_soma  = -550   # µm
L23_LOWER_soma = -1500  # µm

for cellName in cfg.allpops:

    num_cells = cfg.cellNumber[cellName]

    netParams.popParams[cellName] = {
            'cellType':  cellName,
            'cellModel': 'HH_full',
            'numCells':  num_cells,
            # 'xRange': [0, 2*L23_RADIUS],
            # 'zRange': [0, 2*L23_RADIUS],
            # 'yRange': layer['23soma'],
            'xRange': [0, 1],
            'zRange': [0, 1],
            'yRange': [-551,-550],
        }

# print(netParams.popParams)


# #------------------------------------------------------------------------------
# #  extracellular mechs
# #------------------------------------------------------------------------------

if cfg.addExternalStimulation:

    for celltyp in netParams.cellParams.keys():
        label = []
        for secname in netParams.cellParams[celltyp]['secs'].keys():
            netParams.cellParams[celltyp]['secs'][secname]['mechs']['extracellular'] = {}


#------------------------------------------------------------------------------
# addExternalStimulation
#------------------------------------------------------------------------------

if cfg.SinClamp:

    netParams.stimSourceParams['sineStim'] = {'type': 'SinClamp', 'delay': 0.0, 'dur': 4000.0, 
                                              'pkamp': cfg.SinClamp_params['pkamp_Stim'], 
                                              'freq': cfg.SinClamp_params['freq_Stim'], 'phase': 0.0, 
                                              'bias': cfg.SinClamp_params['bias_Stim'],
                                              }
    
    for celltyp in netParams.cellParams.keys():
        netParams.stimTargetParams['sineStim_' + celltyp] = {
            'source': 'sineStim',
            'conds': {'pop': celltyp},
            'sec': 'soma_0',
            'loc': 0.5
        }