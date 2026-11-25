"""
init.py

Starting script to run NetPyNE-basedS1 model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com
"""

import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers
from netpyne import sim
import pickle, json
import numpy as np

from stimulation import make_extracellular_stimuli, make_DC_stimuli, make_DC_disk_stimuli


# cfg, netParams = sim.readCmdLineArgs(simConfigDefault='cfg.py', netParamsDefault='netParams.py')
cfg, netParams = sim.readCmdLineArgs()

sim.initialize(
    simConfig = cfg, 	
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations

## Load cells positions
with open('../data/spkTimes_v9_batch8.pkl', 'rb') as fileObj: simData = pickle.load(fileObj)

cellsTags = simData['cellsTags']

# print(sim.rank,sim.net.cells[0].tags)

for i,metype in enumerate(sim.net.cells):

    if 'presyn' in metype.tags['pop']:
        ii = int(metype.tags['cellLabel'])        
        metype.tags['xnorm'] = cellsTags[ii]['xnorm']
        metype.tags['ynorm'] = cellsTags[ii]['ynorm']
        metype.tags['znorm'] = cellsTags[ii]['znorm']
        metype.tags['x'] = cellsTags[ii]['x']
        metype.tags['y'] = cellsTags[ii]['y']
        metype.tags['z'] = cellsTags[ii]['z']   

    elif 'stimL5' not in metype.tags['pop']:
        ii2 = int(0.000001+(metype.tags['fraction']/(1/cfg.Nmorpho[metype.tags['pop']])))  

        ii = cfg.listmorphonumber[metype.tags['pop']][ii2]

        metype.tags['xnorm'] = cellsTags[ii]['xnorm']
        metype.tags['ynorm'] = cellsTags[ii]['ynorm']
        metype.tags['znorm'] = cellsTags[ii]['znorm']
        metype.tags['x'] = cellsTags[ii]['x']
        metype.tags['y'] = cellsTags[ii]['y']
        metype.tags['z'] = cellsTags[ii]['z']   

sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.net.defineCellShapes()

if cfg.addExternalStimulation:
        #Add extracellular stim
        for c,metype in enumerate(sim.net.cells):
            if metype.tags['cellModel'] == 'HH_full':
                secList = [secs for secs in metype.secs.keys() if "pt3d" in metype.secs[secs]['geom']]
                print("\n", metype.tags, "nsec =",len(secList))
                # print(secList)
                # v_cell_ext, cell = make_extracellular_stimuli(cfg.acs_params, metype, secList)
                # v_cell_ext, cell = make_DC_stimuli(cfg.dc_params, metype, secList)
                v_cell_ext, cell = make_DC_disk_stimuli(cfg.DC_disk_params, metype, secList)

sim.runSim()                      			# run parallel Neuron simulation  

if cfg.addExternalStimulation:
        for c,metype in enumerate(sim.net.cells):
            if metype.tags['cellModel'] == 'HH_full':
                # print("\n", metype.tags)
                metype.t_ext.clear()
                metype.v_ext.clear()

sim.gatherData()                  			# gather spiking data and cell info from each node
sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()           		# plot spikes, V traces, rasters, etc.

