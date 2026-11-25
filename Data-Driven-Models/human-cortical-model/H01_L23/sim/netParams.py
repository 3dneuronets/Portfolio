# =============================================================================
# netParams.py  —  Network Parameters for L23 NetPyNE 
# =============================================================================
import os
import sys
import numpy as np
from netpyne import specs
import pandas as pd
from scipy import stats as st
import h5py
import pickle
from collections import defaultdict
from fixed_network import (
    POP_ORDER,
    read_positions,
    population_layout,
    netpyne_cell_lists,
    read_unique_edges,
    population_conn_lists,
)

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

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

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
# netParams.defaultDelay = 0.1 # default conn delay (ms)
# netParams.propVelocity = 300.0 #  300 μm/ms (Stuart et al., 1997)
# netParams.scaleConnWeightNetStims = 0.001  # weight conversion factor (from nS to uS)

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
                    netParams.cellParams[cellName]['secLists'][secname2][-1] = 'axon_2'    


# =============================================================================
# SECTION 3: Population Parameters (popParams)
# L2/3 spatial geometry from original circuit.py:
#   upper = -250 µm, lower = -1200 µm  (z-axis, soma depth)
#   cylinder radius = 250 µm in x-y
# =============================================================================

position_rows = read_positions(cfg.fixedPositionsFile)

counts, starts = population_layout(position_rows)

assert tuple(cfg.allpops) == POP_ORDER
assert counts == cfg.cellNumber

# Generate cellsList for each population
cell_lists = netpyne_cell_lists(
    position_rows,
    frame=cfg.positionFrame,
    center_x=cfg.sizeX / 2.0,
    center_z=cfg.sizeZ / 2.0,
    top_y=-550.0
)

# Create populations
for cellName in cfg.allpops:

    netParams.popParams[cellName] = {
        'cellType': cellName,
        'cellModel': 'HH_full',
        'cellsList': cell_lists[cellName],
    }

# =============================================================================
# SECTION 3: Synaptic Mechanism Parameters (synMechParams)
# Two main point-process synapses (with STP) + background noise + tonic GABA.
# STP parameters (Dep, Fac, Use, gmax) vary per connection and are overridden
# in connParams using a per-connection synMechParams list.
# =============================================================================

#------------------------------------------------------------------------------
#Import Excel file
circuit_params = pd.read_excel('Circuit_param.xls', sheet_name = None, index_col = 0)


fixed_pairs, duplicate_rows = read_unique_edges(cfg.fixedConnectionsFile, len(position_rows))

fixed_groups = population_conn_lists(position_rows, fixed_pairs)

print('[Fixed Network] Unique connections:',len(fixed_pairs))

print('[Fixed Network] Duplicate file rows removed:', duplicate_rows)


#Get cell names and import biophys
cell_names = [i for i in circuit_params['conn_probs'].axes[0]]

circuit_params["syn_params"] = {'none':{'tau_r_AMPA': 0,'tau_d_AMPA': 0,'tau_r_NMDA': 0,
                                'tau_d_NMDA': 0, 'e': 0,'Dep': 0,'Fac': 0,'Use': 0,'u0':0,'gmax': 0}}
circuit_params["multi_syns"] = {'none':{'loc':0,'scale':0}}

#------------------------------------------------------------------------------

# Ornstein-Uhlenbeck background noise: Gfluct2
# Inserted per-section via custom function in init.py; listed here for reference.
netParams.synMechParams['Gfluct2'] = {
    'mod':   'Gfluct2',
    'E_e':   0.0,
    'E_i':   -80.0,
    'g_e0':  0.0,
    'g_i0':  0.0,
    'std_e': 0.0,
    'std_i': 0.0,
    'tau_e': 65.0,
    'tau_i': 20.0,
}

# Tonic GABA: tonic.mod  (steady-state shunting conductance)
# Inserted as distributed mechanism in init.py; listed here for reference.
netParams.synMechParams['TonicGABA'] = {
    'mod':    'tonic',
    'e_gaba': -75.0,
}

# =============================================================================
# SECTION 4: Connectivity Parameters (connParams)
# One rule per (pre, post) pair = up to 16 rules (skip zero-prob pairs).
#
# Synaptic target section determined by SYN_POS index:
#   0 → apic + dend  (split into two sub-rules, each at prob * 0.5)
#   1 → apical
#   2 → basal (dend)
#   3 → basal (dend, proximal-biased in original; approximated as uniform here)
#
# Per-connection STP parameters override the base synMechParams defaults.
# =============================================================================

#------------------------------------------------------------------------------
# SynMechParams
#------------------------------------------------------------------------------

for pre in cfg.allpops:
    for post in cfg.allpops:
        
        Syn_pos = int(circuit_params['Syn_pos'].at[pre, post])


        if (pre, post) in fixed_groups:

            if "PYR" in pre: # Excitatory
                netParams.synMechParams[pre+post] = {'mod': 'ProbAMPANMDA',
                                                        'tau_r_AMPA': 0.3, 'tau_d_AMPA': 3.0, 'tau_r_NMDA': 2.0,
                                                        'tau_d_NMDA': 65.0,
                                                        'e':          0.0,
                                                        'u0':         0.0,
                                                        'Dep': circuit_params["Depression"].at[pre, post],
                                                        'Fac': circuit_params["Facilitation"].at[pre, post],
                                                        'Use': circuit_params["Use"].at[pre, post],
                                                        'gmax': cfg.couplings[f'{pre}->{post}'] * circuit_params["syn_cond"].at[pre, post],
                                                        }
                if int(circuit_params['Syn_pos'].at[pre, post]) == 0:
                    netParams.synMechParams[pre+post]['gmax'] = cfg.couplings[f'{pre}->{post}'] * cfg.gExc*circuit_params["syn_cond"].at[pre, post]
                    #print("correction factor applied in Exc-Exc coonections gmax*= ", cfg.gExc)                                
            else:
                netParams.synMechParams[pre+post] = {'mod': 'ProbUDFsyn',
                                                        'tau_r': 1, 'tau_d': 10,
                                                        'e':     -80.0,
                                                        'u0':    0.0,
                                                        'Dep': circuit_params["Depression"].at[pre, post],
                                                        'Fac': circuit_params["Facilitation"].at[pre, post],
                                                        'Use': circuit_params["Use"].at[pre, post],
                                                        'gmax': cfg.couplings[f'{pre}->{post}'] * circuit_params["syn_cond"].at[pre, post],
                                                    }


# =============================================================================
# Validation current clamp
# =============================================================================

if cfg.IClamp_val_act:
    for pop in cfg.allpops:

        source = f'IClamp_{pop}'

        netParams.stimSourceParams[source] = {
            'type': 'IClamp',
            'del': cfg.IClamp_delay,
            'dur': cfg.IClamp_dur,
            'amp': cfg.IClamp_amp[pop],
        }

        netParams.stimTargetParams[f'{source}->{pop}'] = {
            'source': source,
            'conds': {'pop': pop},
            'sec': 'soma_0',
            'loc': 0.5,
        }

#########################################


# ============================================================
# FIXED CONNECTIVITY FROM DAT FILE
# ============================================================

expected_contacts = 0

for (pre, post), conn_list in fixed_groups.items():

    # --------------------------------------------------------
    # Number of synaptic contacts from Excel
    # --------------------------------------------------------

    value = float(circuit_params['n_cont'].at[pre, post])
    if value < 1.0:
        value = 1.0

    if not np.isfinite(value) or value < 1 or not value.is_integer():
        raise ValueError(f'Invalid n_cont for {pre}->{post}: {value}')

    n_synapses = int(value)

    # --------------------------------------------------------
    # Postsynaptic compartment
    # Preserve original Syn_pos convention
    # --------------------------------------------------------

    syn_pos = int(circuit_params['Syn_pos'].at[pre, post])

    if syn_pos == 0:

        target_sec = 'spiny'

    elif syn_pos == 1:

        target_sec = 'apical'

    elif syn_pos in (2, 3):

        target_sec = 'basal'

    else:
        raise ValueError(f'Invalid Syn_pos for {pre}->{post}: {syn_pos}')

    # --------------------------------------------------------
    # Create NetPyNE connectivity rule
    # --------------------------------------------------------

    label = f'fixed_{pre}->{post}'

    netParams.connParams[label] = {

        'preConds': {'pop': pre},

        'postConds': {'pop': post},

        # Explicit connectivity
        'connList': conn_list,

        # Existing synaptic mechanism
        'synMech': pre + post,

        # Synaptic contacts per connected neuron pair
        'synsPerConn': n_synapses,

        'weight': 1.0,

        'delay': 0.5,

        'sec': target_sec,
    }

    expected_contacts += len(conn_list) * n_synapses

print('[Fixed Network] Expected synaptic contacts:',expected_contacts)