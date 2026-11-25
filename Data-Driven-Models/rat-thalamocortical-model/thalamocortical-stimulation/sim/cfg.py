"""
cfg.py 

Simulation configuration for S1-thalamus model (using NetPyNE)
This file has sim configs as well as specification for parameterized values in netParams.py 

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""

from netpyne import specs
import pickle
import os
import numpy as np

cfg = specs.SimConfig()  

#------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
#------------------------------------------------------------------------------

cfg.simType='S1_TH'
cfg.coreneuron = False

#------------------------------------------------------------------------------
# Run parameters
#------------------------------------------------------------------------------
cfg.duration = 1.2*1e4 ## Duration of the sim, in ms  
cfg.dt = 0.05
cfg.seeds = {'cell': 4322, 'conn': 4322, 'stim': 4322, 'loc': 4322} 
cfg.hParams = {'celsius': 34, 'v_init': -65}  
cfg.verbose = False
cfg.createNEURONObj = True
cfg.createPyStruct = True  
cfg.cvode_active = False
cfg.cvode_atol = 1e-6
cfg.cache_efficient = True
cfg.printRunTime = 0.1

cfg.includeParamsLabel = False
cfg.printPopAvgRates = True
cfg.checkErrors = False

#------------------------------------------------------------------------------
# Cells
#------------------------------------------------------------------------------
cfg.rootFolder = os.getcwd()

# Load cells info from previously saved using netpyne (False: load from HOC BBP files, slower)
cfg.loadcellsfromJSON = True

cfg.poptypeNumber = 61 # max 55 + 6
cfg.celltypeNumber = 213 # max 207 + 6

cfg.cao_secs = 1.2

cfg.use_frac = {} # use[invivo] = cfg.use_frac * use[invitro]

cfg.use_frac['EIproximal'] = 0.75 # shallow dependence between PC-proximal targeting cell types (LBCs, NBCs, SBCs, ChC)
cfg.use_frac['Inh'] = 0.50 # Pathways that had not been studied experimentally were assumed to have an intermediate level of dependence
cfg.use_frac['EE'] = 0.25 # steep Ca2+ dependence for connections between PC-PC and PC-distal targeting cell types (DBC, BTC, MC, BP)
cfg.use_frac['EIdistal'] = 0.25 

# TO DEBUG - import and simulate only the Cell soma (to study only the Net)
cfg.reducedtest = False    

#------------------------------------------------------------------------------  
#------------------------------------------------------------------------------  
# S1 Cells
# Load 55 Morphological Names and Cell pop numbers -> L1:6 L23:10 L4:12 L5:13 L6:14
# Load 207 Morpho-electrical Names used to import the cells from 'cell_data/' -> L1:14 L23:43 L4:46 L5:52 L6:52
# Create [Morphological,Electrical] = number of cell metype in the sub-pop

with open('cells/S1-cells-distributions-Rat.txt') as mtype_file:
    mtype_content = mtype_file.read()       

cfg.popNumber = {}
cfg.cellNumber = {} 
cfg.popLabel = {} 
popParam = []
cellParam = []
cfg.meParamLabels = {} 
cfg.popLabelEl = {} 
cfg.cellLabel = {}

for line in mtype_content.split('\n')[:-1]:
    cellname, mtype, etype, n, m = line.split()
    metype = mtype + '_' + etype[0:3]
    cfg.cellNumber[metype] = int(n)
    cfg.popLabel[metype] = mtype
    cfg.popNumber[mtype] = int(m)
    cfg.cellLabel[metype] = cellname

    if mtype not in popParam:
        popParam.append(mtype)
        cfg.popLabelEl[mtype] = [] 
               
    cfg.popLabelEl[mtype].append(metype)
    
    cellParam.append(mtype + '_' + etype[0:3])
    
cfg.S1pops = popParam[0:55]
cfg.S1cells = cellParam

# cfg.S1pops = ['L5_SBC', 'L5_TTPC2', 'L6_SBC', 'L6_TPC_L4']

cfg.S1cells = []
for metype in cellParam:
    if cfg.popLabel[metype] in cfg.S1pops:        
        cfg.S1cells.append(metype)
	    
   
popParam = []
cellParam = []
for metype in cfg.S1cells:
    cellParam.append(metype)
    
for mtype in cfg.S1pops:
    popParam.append(mtype)    

# print(cfg.S1pops)
# print(cfg.S1cells)

#------------------------------------------------------------------------------  
# Thalamic Cells

cfg.thalamicpops = ['ss_RTN_m', 'VPM_sTC', 'VPM_TC']

cfg.cellNumber['ss_RTN_m'] = int(382 * (210**2/150**2))# from mouse model (r = 150 um)
cfg.cellNumber['VPM_sTC'] = int(0.5 * 839 * (210**2/150**2))
cfg.cellNumber['VPM_TC'] = int(0.5 * 839 * (210**2/150**2))

for mtype in cfg.thalamicpops: # No diversity
	metype = mtype
	popParam.append(mtype)
	cfg.popLabel[metype] = mtype
	cellParam.append(metype)

	cfg.popNumber[mtype] = cfg.cellNumber[metype]

#------------------------------------------------------------------------------  
cfg.popParamLabels = popParam
cfg.cellParamLabels = cellParam

#------------------------------------------------------------------------------
# Network 
#------------------------------------------------------------------------------
cfg.scale = 1.0 # reduce size
cfg.sizeY = 2082.0
cfg.sizeX = 420.0 # r = 210 um and hexagonal side length = 230.9 um
cfg.sizeZ = 420.0
cfg.scaleDensity = 1.0 # Number of cells = 31346

for metype in cfg.S1cells:
    cfg.cellNumber[metype] = int(np.ceil(cfg.scaleDensity*cfg.cellNumber[metype]))
    # print(metype, cfg.cellNumber[metype])

#--------------------------------------------------------------------------
# Recording 
#--------------------------------------------------------------------------
cfg.allpops = cfg.cellParamLabels
cfg.cellsrec = 2
if cfg.cellsrec == 0:  cfg.recordCells = cfg.allpops # record all cells
elif cfg.cellsrec == 1: cfg.recordCells = [(pop,0) for pop in cfg.allpops] # record one cell of each pop
elif cfg.cellsrec == 2: # record one cell of each cellMEtype 
    cfg.recordCells = []
    for metype in cfg.cellParamLabels:
        if cfg.cellNumber[metype] < 5:
            for numberME in range(cfg.cellNumber[metype]):
                cfg.recordCells.append((metype,numberME))
        else:
            numberME = 0
            diference = cfg.cellNumber[metype] - 5.0*int(cfg.cellNumber[metype]/5.0)
            
            for number in range(5):            
                cfg.recordCells.append((metype,numberME))
                
                if number < diference:              
                    numberME+=int(np.ceil(cfg.cellNumber[metype]/5.0))  
                else:
                    numberME+=int(cfg.cellNumber[metype]/5.0)

cfg.recordTraces = {'V_soma': {'sec':'soma', 'loc':0.5, 'var':'v'}}  ## Dict with traces to record
cfg.recordStim = False			
cfg.recordTime = False  		
cfg.recordStep = 0.1           

# cfg.recordLFP = [[xz, y, xz] for xz in [105, 500] for y in [500, 1000, 1500, 2000]] #

# cfg.recordLFP = [[xz, y, xz] for xz in [0] for y in [500, 2000]] 

# print(cfg.recordCells)
#------------------------------------------------------------------------------
# Saving
#------------------------------------------------------------------------------
cfg.simLabel = 'v0_batch0'
cfg.saveFolder = '../data/'+cfg.simLabel
# cfg.filename =                	## Set file output name
cfg.savePickle = True         	## Save pkl file
cfg.saveJson = False	           	## Save json file
cfg.saveDataInclude = ['simData', 'simConfig', 'netParams', 'net'] ## , 'simConfig', 'netParams'
cfg.backupCfgFile = None 		##  
cfg.gatherOnlySimData = False	##  
cfg.saveCellSecs = False			
cfg.saveCellConns = False	

#------------------------------------------------------------------------------
# Analysis and plotting 
# ------------------------------------------------------------------------------
cfg.analysis['plotRaster'] = {'include': cfg.allpops, 'saveFig': True, 'showFig': False, 'orderInverse': True, 'timeRange': [0,cfg.duration], 
                              'figSize': (24,12), 'popRates': False, 'fontSize':12, 'lw': 1, 'markerSize':2, 'marker': '.', 'dpi': 100} 
cfg.analysis['plot2Dnet']   = {'include': cfg.allpops, 'saveFig': True, 'showConns': False, 'figSize': (24,24), 'fontSize':8}   # Plot 2D cells xy
cfg.analysis['plotTraces'] = {'include': cfg.recordCells, 'oneFigPer': 'cell', 'overlay': True, 'timeRange': [8000,cfg.duration], 'ylim': [-100,50], 'saveFig': True, 'showFig': False, 'figSize':(12,4)}
# cfg.analysis['plotLFP'] = {'separation': 1.0, 'plots': ['timeSeries', 'spectrogram'], 'timeRange': [8000,cfg.duration], 'maxFreq': 500, 'saveFig': True, 'showFig': False}
# cfg.analysis['plot2Dfiring']={'saveFig': True, 'figSize': (24,24), 'fontSize':16}
# cfg.analysis['plotConn'] = {'includePre': cfg.allpops, 'includePost': cfg.allpops, 'feature': 'numConns', 'groupBy': 'pop', 'figSize': (12,12), 
                            # 'saveFig': True, 'orderBy': 'gid', 'graphType': 'matrix', 'saveData':'../data/matrix_numConn.json', 'fontSize': 18}
# cfg.analysis['plotConn'] = {'includePre': ['L1_DAC_cNA','L23_MC_cAC','L4_SS_cAD','L4_NBC_cNA','L5_TTPC2_cAD', 'L5_LBC_cNA', 'L6_TPC_L4_cAD', 'L6_LBC_cNA', 'ss_RTN_o', 'ss_RTN_m', 'ss_RTN_i', 'VPL_sTC', 'VPM_sTC', 'POm_sTC_s1'], 'includePost': ['L1_DAC_cNA','L23_MC_cAC','L4_SS_cAD','L4_NBC_cNA','L5_TTPC2_cAD', 'L5_LBC_cNA', 'L6_TPC_L4_cAD', 'L6_LBC_cNA', 'ss_RTN_o', 'ss_RTN_m', 'ss_RTN_i', 'VPL_sTC', 'VPM_sTC', 'POm_sTC_s1'], 'feature': 'convergence', 'groupBy': 'pop', 'figSize': (24,24), 'saveFig': True, 'orderBy': 'gid', 'graphType': 'matrix', 'fontSize': 18}
# cfg.analysis['plot2Dnet']   = {'include': ['L5_LBC', 'VPM_sTC', 'POm_sTC_s1'], 'saveFig': True, 'showConns': True, 'figSize': (24,24), 'fontSize':16}   # Plot 2D net cells and connections
# cfg.analysis['plotShape'] = {'includePre': cfg.recordCells, 'includePost': cfg.recordCells, 'showFig': False, 'includeAxon': False, 
                            # 'showSyns': False, 'saveFig': True, 'dist': 0.55, 'cvar': 'voltage', 'figSize': (24,12), 'dpi': 600}

#------------------------------------------------------------------------------
# Spontaneous synapses + background - data from Rat
#------------------------------------------------------------------------------
cfg.addStimSynS1 = True
cfg.rateStimE = 9.0
cfg.rateStimI = 9.0

#------------------------------------------------------------------------------
# Connectivity
#------------------------------------------------------------------------------
## S1->S1
cfg.addConn = True

cfg.synWeightFractionEE = [1.0, 1.0] # E -> E AMPA to NMDA ratio
cfg.synWeightFractionEI = [1.0, 1.0] # E -> I AMPA to NMDA ratio
cfg.synWeightFractionII = [1.0, 1.0]  # I -> I GABAA to GABAB ratio
cfg.synWeightFractionIE = [1.0, 1.0]  # I -> E GABAA to GABAB ratio
cfg.EEGain = 1.0
cfg.EIGain = 1.0
cfg.IIGain = 1.0
cfg.IEGain = 1.0

#------------------------------------------------------------------------------
## Th->Th 
cfg.connectTh = True
cfg.connect_RTN_RTN     = True
cfg.connect_TC_RTN      = True
cfg.connect_RTN_TC      = True

cfg.yConnFactor             = 10 # y-tolerance form connection distance based on the x and z-plane radial tolerances (1=100%; 2=50%; 5=20%; 10=10%)

cfg.intraThalamicGain = 1.0 

cfg.connWeight_RTN_RTN      = 2.0 # optimized to increase synchrony
cfg.connWeight_TC_RTN       = 1.5 # optimized to increase synchrony
# cfg.connWeight_RTN_TC       = 0.35 # optimized to increase synchrony
cfg.connWeight_RTN_TC       = 1.5 # optimized to decrease synchrony

cfg.connProb_RTN_RTN        = 0.5 #2021-06-23 - test
cfg.connProb_TC_RTN         = 0.9 #2021-06-23 - test
cfg.connProb_RTN_TC         = 0.9 #2021-06-23 - test

cfg.divergenceHO = 10

#------------------------------------------------------------------------------
## Th->S1
cfg.connect_Th_S1 = True
cfg.TC_S1 = {}
cfg.TC_S1['VPL_sTC'] = True
cfg.TC_S1['VPM_sTC'] = True
cfg.TC_S1['POm_sTC_s1'] = True

cfg.frac_Th_S1 = 1.0
#------------------------------------------------------------------------------
## S1->Th 
cfg.connect_S1_Th = False

cfg.connect_S1_RTN = True
cfg.convergence_S1_RTN         = 30.0  # dist_2D<R
cfg.connWeight_S1_RTN       = 0.500

cfg.connect_S1_TC = True
cfg.convergence_S1_TC         = 30.0  # dist_2D<R
cfg.connWeight_S1_TC       = 0.250

#------------------------------------------------------------------------------
# Current inputs 
#------------------------------------------------------------------------------
cfg.addIClamp = True  
 
cfg.thalamocorticalconnections =  ['VPM_sTC']

cfg.IClamp = []
cfg.IClampnumber = 0

#------------------------------------------------------------------------------
## decrease transient
cfg.IClamp.append({'pop': 'VPM_sTC', 'sec': 'soma', 'loc': 0.5, 'start': 0, 'dur': 5, 'amp': 5.0}) #pA
cfg.IClampnumber=cfg.IClampnumber+1

cfg.IClamp.append({'pop': 'VPM_TC', 'sec': 'soma', 'loc': 0.5, 'start': 5, 'dur': 5, 'amp': 5.0}) #pA
cfg.IClampnumber=cfg.IClampnumber+1
    
#------------------------------------------------------------------------------
## Simgle Pulse (IPI = 2 sec)
# for stimOPT in range(2):
#     cfg.IClamp.append({'pop': 'VPM_sTC', 'sec': 'soma', 'loc': 0.5, 'start': 9000+stimOPT*2000, 'dur': 25, 'amp': -0.1}) #pA
#     cfg.IClampnumber=cfg.IClampnumber+1

#------------------------------------------------------------------------------
## Rhythmic
for stimOPT in range(20):
    cfg.IClamp.append({'pop': 'VPM_sTC', 'sec': 'soma', 'loc': 0.5, 'start': 9000+stimOPT*100, 'dur': 25, 'amp': -0.1}) #pA
    cfg.IClampnumber=cfg.IClampnumber+1

#------------------------------------------------------------------------------
## Non-Rhythmic
# time = 0
# cfg.IClamp.append({'pop': 'VPM_sTC', 'sec': 'soma', 'loc': 0.5, 'start': 9000+time, 'dur': 25, 'amp': -0.1}) #pA
# cfg.IClampnumber=cfg.IClampnumber+1
# #print(9000+time)

# interval_time = [63, 83, 63, 59, 88, 104, 80, 79, 71, 67, 111, 83, 56,138, 52, 58, 68, 64, 86, 69, 51, 65, 66, 87, 68, 62, 60, 
#                  73, 75, 50, 132, 53, 52, 56,108, 83, 77, 60, 100, 58, 106, 61, 68, 56, 58, 53, 53, 77, 59, 91, 137, 57, 67, 68, 
#                  53, 62, 62, 54, 55, 64, 92, 86, 53,139, 68, 95, 51, 58, 67, 69, 120, 60,129,116, 66, 108, 55, 55, 58, 97, 60, 
#                  66, 51, 61, 56, 70, 71, 55,112, 100, 94, 73, 55, 55,120, 73, 66, 72, 61, 62]

# interval_time = np.array(interval_time)+25

# randomly_chosen_20elements = np.random.choice(interval_time, size=19, replace=False)

# for t in randomly_chosen_20elements:
#     time=time+t
#     cfg.IClamp.append({'pop': 'VPM_sTC', 'sec': 'soma', 'loc': 0.5, 'start': 9000+time, 'dur': 25, 'amp': -0.1}) #pA
#     cfg.IClampnumber=cfg.IClampnumber+1
   # print(9000+time)

# print(cfg.IClampnumber)
# print(cfg.IClamp)
