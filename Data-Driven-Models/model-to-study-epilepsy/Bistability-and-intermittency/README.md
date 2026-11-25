# From bistability to intermittency: linking synaptic variability and slow potassium currents to spontaneous seizures generation

This repository contains the code and resources associated with the manuscript  
*"From bistability to intermittency: biophysical mechanisms of spontaneous seizures in a neuronal model"*.

In this work, we investigate how spontaneous seizure-like events emerge in a conductance-based neuronal network model. In particular, we show that the interplay between excitation and inhibition shapes the transition from bistable dynamics to intermittency, allowing the spontaneous alternation between physiological and pathological activity. Our results indicate that stronger inhibition increases the variability of the postsynaptic potential (PSP), and that the intermittent regime is also associated with marked changes in the temporal structure of the slow potassium current.

The repository is organized into three main components:

1. **Conductance-based model (C code)**  
   Simulates the neuronal network dynamics used in the manuscript and reproduces representative results from the paper, including *Figure 4(a)*.

2. **Seizure detection using recurrence analysis (Python)**  
   Implements the seizure detection method based on recurrence analysis of the PSP time series.

3. **Microstates maximum entropy function (Python)**  
   Provides the routines used to compute the maximum entropy of recurrence microstates from a time series. Although developed for this project, this script can also be applied to other types of data.

Instructions for running the code and modifying parameters are provided below.

> **Citation:** If you use this repository in your work, please cite our paper. The DOI will be added upon publication.

---

## Repository Overview

This repository was created to accompany the manuscript and to make the main computational tools reproducible and reusable. The focus is on three central elements of the study:

- simulation of seizure-like dynamics in a biophysical neuronal network,
- detection of spontaneous seizure events from the PSP signal,
- quantification of dynamical changes through recurrence microstates and maximum entropy.

---

## 1. Neuronal Model Simulation

The network simulations were implemented in **C**. In this repository, we provide an example code that reproduces the simulation used to generate *Figure 4(a)* of the manuscript.

### Requirements

- A C compiler such as `gcc` or `icc`

### Output

Running the simulation produces a `.dat` file containing:

- **Postsynaptic potential** (`PSP`)

### Notes on simulation time

By default, the code simulates **250 seconds** of network activity. Depending on the simulation length and your CPU performance, the runtime may range from a few minutes to several hours.

We recommend first running a shorter simulation to test the setup, and then increasing the simulation time for longer analyses.

### Adjustable parameters

The code can be modified to explore different dynamical regimes by changing parameters such as:

- **simulation time**
- **coupling strength**
- **synaptic balance**
- **other model parameters**

This allows the user to investigate how parameter changes affect the transition between different dynamical regimes, including bistability and intermittency.

---

## 2. Seizure Detection Using Recurrence Analysis

The repository also includes Python scripts for seizure detection based on recurrence analysis of the PSP signal.

The detection method is based on the temporal evolution of the **maximum entropy of recurrence microstates**, which is computed in sliding windows of the time series. In the manuscript, this quantity is used to identify seizure-like up states from spontaneous network activity.

This part of the repository is useful both for reproducing the analysis from the paper and for applying the same methodology to other simulated or experimental signals.

---

## 3. Microstates Maximum Entropy

The file `Microstates_Maximum_Entropy.py` contains the functions required to compute the **maximum entropy of recurrence microstates** from a given time series.

This script is a core component of the seizure detection pipeline and is required for the analysis notebook and related scripts. More generally, it can also be used independently for recurrence-based analysis of other data.

---

## Visualization and Analysis

A Jupyter notebook, `Detection_plots.ipynb`, is included for visualization and analysis of the simulation output.

This notebook can be used to:

- load the simulated PSP data,
- compute recurrence-based measures,
- apply the seizure detection procedure,
- visualize the detected events.

To run the notebook correctly, make sure that `Microstates_Maximum_Entropy.py` is available in the same environment, since it contains the functions required for the computation of the microstates maximum entropy used in the detection pipeline.

---

## Usage

A typical workflow is:

1. Run the **C simulation** to generate the PSP time series.
2. Use the **Python scripts** to compute recurrence microstates and maximum entropy.
3. Apply the **seizure detection method** to identify seizure-like events.
4. Use the **Jupyter notebook** for visualization and further analysis.

---

## Availability

This repository is intended to support the reproducibility of the manuscript and to provide reusable tools for the analysis of spontaneous seizure dynamics in neuronal models.

---
