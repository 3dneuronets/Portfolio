# The Roles of Potassium and Calcium Currents in the Bistable Firing Transition

**Computational Neuroscience | Biophysical Neuron Models | Ion Channels | Network Dynamics**

## Overview

This repository contains the computational models, simulation scripts, and analysis notebooks associated with the study **"The Roles of Potassium and Calcium Currents in the Bistable Firing Transition"**, published in *Brain Sciences* (2023).

The project investigates the contribution of potassium and calcium ionic currents to transitions between different neuronal firing states.

Using biophysically based neuronal models and network simulations, the study explores how intrinsic membrane mechanisms influence neuronal excitability, firing patterns, and collective network dynamics.

The repository provides two levels of computational investigation:

- **Single-neuron simulations:** Investigation of membrane responses and the effects of specific ionic currents on neuronal firing.
- **Neuronal network simulations:** Investigation of collective activity, synchronization, and firing patterns in interconnected neurons.

## Scientific Background

Neuronal activity depends on the interaction of voltage-gated ionic conductances, membrane properties, and synaptic inputs.

Potassium and calcium currents play important roles in regulating neuronal excitability, spike-frequency adaptation, and firing-state transitions.

Bistability occurs when a dynamical system can exhibit two stable activity states under the same parameter conditions, with transitions between them depending on the system's state and perturbations.

Understanding these mechanisms is relevant to neuronal dynamics and the investigation of pathological synchronization.

## Computational Methods

### Single-Neuron Modeling

The single-neuron simulations examine membrane dynamics and firing responses using biophysically based neuron models.

The repository includes a Jupyter notebook titled **"Model of regular spiking neuron with slow Potassium Current for spike-frequency adaptation"**.

This example illustrates the influence of slow potassium currents on firing patterns and corresponds to Figure 1(A) of the publication.

### Network Simulations

The network implementation uses **NetPyNE** and **NEURON** to define and simulate neuronal populations.

The simulations can be configured to investigate:

- Neuronal excitability and firing patterns
- Ionic current contributions to neuronal dynamics
- Recurrent network interactions
- Synchronization and collective activity
- Parameter-dependent firing-state transitions

Network configuration and neuron populations are defined separately from simulation execution settings, allowing systematic parameter exploration.

## Repository Structure

```text
BistabilityHH/
├── data/
│   └── Simulation outputs and figures
├── sim/
│   └── Simulation-related files
├── simulations_one_cell/
│   └── Single-neuron models and notebooks
├── simulations_network/
│   └── Network models and simulation files
├── requirements.txt
└── README.md
```

The single-neuron and network directories contain the simulation-specific models and required NEURON mechanisms.

## Requirements

The implementation uses:

- Python
- NEURON
- NetPyNE
- C/C++ compilation tools for NMODL mechanisms
- Jupyter Notebook
- Python scientific-computing libraries listed in `requirements.txt`
- Open MPI for supported parallel simulation workflows

A Python virtual environment or Conda environment is recommended to isolate the required software.

## How to Run
First compile the mods with  nrnivmodl from NEURON mechanism library.

### 1. Single-Neuron Simulations

Navigate to the `simulations_one_cell/` directory.

Open the Jupyter notebook demonstrating the regular-spiking neuron with slow potassium current.

Select the Python environment containing the required packages and compiled NEURON mechanisms.

Execute the notebook cells to generate the model responses and associated figures.

### 2. Network Simulations

Navigate to the network simulation directory.

The network implementation uses:

| File | Description |
|---|---|
| `cfg.py` | Simulation duration, recording settings, and experimental conditions |
| `netParams.py` | Neuronal populations, biophysical mechanisms, and connectivity |
| `init.py` | Network creation, simulation execution, and analysis |

Configure the simulation and network parameters in the corresponding files.

From the directory containing `init.py`, run:

```bash
python3 init.py
```

For repeated simulations, use the parameter-sweep workflow provided by the relevant scripts if available.

## Analysis and Outputs

The code can be used to investigate the relationship between intrinsic neuronal dynamics and collective network activity.

Typical outputs include:

- Neuronal membrane voltage traces
- Single-neuron firing patterns
- Spike raster plots
- Network connectivity visualizations
- Simulation data saved for subsequent analysis

The repository's original instructions identify `data/v0_batch1/` as an example default results directory.

Simulation data may be stored in Python pickle files together with generated figures.

## Reproducibility Notes

- NMODL mechanisms must be compiled before running simulations that depend on them.
- Different NEURON and NetPyNE versions may require compatibility adjustments.
- Reproducing publication figures requires the appropriate simulation parameters and input conditions.
- Results should be compared with the corresponding publication figures before treating the setup as validated.
- A dedicated requirements file with tested package versions would improve long-term reproducibility.

## Scientific Reference

Borges, F. S., Protachevicz, P. R., Souza, D. L. M., et al. (2023). **The Roles of Potassium and Calcium Currents in the Bistable Firing Transition.** *Brain Sciences*, 13(9), 1347.

https://doi.org/10.3390/brainsci13091347
