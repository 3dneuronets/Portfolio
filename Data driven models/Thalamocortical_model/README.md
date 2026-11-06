# Thalamocortical Circuit Modeling with External Stimulation

**Data-Driven Models | Thalamocortical Networks | NetPyNE | Neural Stimulation**

## Overview

This repository provides a computational implementation of a **biophysically detailed thalamocortical network model with external stimulation control**, developed using NetPyNE and NEURON.

The project extends the modeling framework described in **"Large-scale biophysically detailed model of somatosensory thalamocortical circuits in NetPyNE"**, published in *Frontiers in Neuroinformatics* (2022).

The simulations provide a framework for investigating the activity of interconnected cortical and thalamic neuronal populations and their responses to external stimulation.

The implementation combines biologically detailed neuronal models, synaptic connectivity, and simulation-based analysis of network dynamics.

## Scientific Background

Thalamocortical circuits play an important role in sensory information processing and the generation of coordinated neuronal activity.

Their dynamics emerge from interactions between multiple neuronal populations, intrinsic membrane properties, synaptic mechanisms, and external inputs.

Biophysically detailed computational models provide a way to investigate these interactions and explore how stimulation protocols influence neuronal firing and network activity.

This project builds on an experimentally informed model of somatosensory thalamocortical circuitry and introduces stimulation-related configurations for investigating network responses.

## Model Overview

The model uses NetPyNE to organize network construction and NEURON to simulate neuronal membrane dynamics.

The underlying thalamocortical modeling framework includes:

- Multiple cortical and thalamic neuronal populations
- Multicompartmental neurons with biophysical membrane mechanisms
- Excitatory and inhibitory synaptic interactions
- Population-specific connectivity
- Background and external inputs
- Network-level recording and analysis

The stimulation implementation enables the study of network responses under different externally driven conditions.

## Computational Methods

### Network Construction

NetPyNE is used to define neuronal populations, cellular properties, synaptic mechanisms, and connectivity rules.

The implementation separates network parameters from simulation configuration, facilitating changes in stimulation conditions and other model parameters.

### External Stimulation

The model incorporates external stimulation into the thalamocortical simulation framework.

Stimulation parameters and experimental conditions should be configured using the corresponding files in the `sim/` directory.

The precise stimulation targets, amplitudes, timing, and other parameters depend on the configuration selected by the researcher.

### Network Dynamics

The simulation framework supports investigation of:

- Neuronal firing and membrane potential responses
- Population activity and synchronization
- Changes in firing patterns under stimulation
- Thalamocortical network interactions
- Responses to different simulation conditions

## Repository Structure

```text
Thalamocortical_Circuit_Stimulation/
├── data/
│   └── Simulation results and figures
├── sim/
│   ├── init.py
│   ├── cfg.py
│   ├── netParams.py
│   ├── batch.py
│   ├── cells/
│   └── mod/
├── requirements.txt
└── README.md
```

### Main Simulation Files

| File or Directory | Description |
|---|---|
| `sim/init.py` | Main network initialization and simulation execution |
| `sim/cfg.py` | Simulation parameters, stimulation conditions, and recording settings |
| `sim/netParams.py` | Neuronal populations, cell properties, and network connectivity |
| `sim/batch.py` | Execution of simulation batches |
| `sim/cells/` | Neuronal cell models and associated definitions |
| `sim/mod/` | NMODL ionic-channel and synaptic mechanisms |
| `data/` | Saved simulation outputs and figures |

## Requirements

The project requires a compatible installation of:

- Python
- NEURON with Python support
- NetPyNE
- A C/C++ compiler for NEURON mechanisms
- Open MPI for parallel execution
- Python scientific-computing packages listed in `requirements.txt`
- Jupyter Notebook for interactive model examples

A dedicated Python environment is recommended.

## How to Run

First, from the simulation directory:

```bash
cd sim
nrnivmodl mod
```

This compiles the NMODL mechanisms used by the neuronal and synaptic models.


### 1. Configure the Simulation

Edit `sim/cfg.py` to select simulation parameters, recording options, stimulation conditions, and output settings.

For the documented standard NEURON execution mode, ensure:

```python
cfg.coreneuron = False
```

Changes to neuronal populations, connection rules, or synaptic properties can be made in `netParams.py`.

### 2. Run the Network

From the `sim/` directory, execute:

```bash
python batch.py
```

For MPI execution, the original repository documents:

```bash
mpiexec -n 4 nrniv -python -mpi init.py
```

Adjust the number of MPI processes according to your computational environment.

### 3. Run Single-Neuron Examples

The repository also documents an interactive single-cell model workflow.

Open the corresponding notebook, select the environment containing NEURON and the required dependencies, and run the notebook cells.

### 4. Analyze Simulation Results

The simulation saves outputs according to the configuration defined in `cfg.py`.

The resulting activity can be examined to investigate neuronal firing, responses to stimulation, and population-level dynamics.

## Analysis and Outputs

Depending on the selected configuration, simulation outputs may include:

- Spike trains and raster plots
- Membrane potential recordings
- Population firing statistics
- Network architecture visualizations
- Stimulation-response comparisons
- Saved simulation data for further processing

The exact generated files depend on the configured recording and analysis options.

## Reproducibility Notes

- Compile NMODL mechanisms before executing the network.
- Verify compatibility between the installed NEURON and NetPyNE versions.
- Use the appropriate configuration to reproduce a particular stimulation condition.
- The repository is a stimulation-oriented extension of the published thalamocortical model, not a separate experimental reconstruction of all its biological parameters.
- Results should be compared with the original publication and project-specific stimulation configurations.
- The source model and its scientific references should be credited when reusing or adapting this implementation.

## Scientific Reference

Borges, F. S., Moreira, J. V. S., Takarabe, L. M., Lytton, W. W., & Dura-Bernal, S. (2022). **Large-scale biophysically detailed model of somatosensory thalamocortical circuits in NetPyNE.** *Frontiers in Neuroinformatics*, 16.

https://doi.org/10.3389/fninf.2022.884245

