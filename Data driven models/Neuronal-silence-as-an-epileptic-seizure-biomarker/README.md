# Neuronal Silence as a Predictive Biomarker for Epileptic Seizures

**Computational Neuroscience | Epilepsy | Seizure Biomarkers | Machine Learning**

## Overview

This repository contains computational simulations and analysis code associated with the study **"Neuronal silence as a predictive biomarker and target for epileptic seizures suppression"**, published in *Scientific Reports* (2026).

The study investigates the relationship between neuronal firing patterns, network synchronization, and seizure-like activity, focusing on prolonged periods of neuronal silence preceding pathological synchronization.

Using conductance-based neuronal network simulations, the research introduces **mean silence time** as a potential biomarker for anticipating transitions into highly synchronized states. The study also investigates stimulation-based seizure suppression in computational models and examines the relevance of neuronal silence using human electrophysiological recordings.

The repository provides two complementary computational workflows:

- **Neuronal network simulations in C:** Investigation of spontaneous network dynamics, synchronization, spike irregularity, and neuronal silence.
- **Machine learning analysis in Python:** Random Forest modeling using mean silence time to predict subsequent changes in network synchronization.

## Scientific Background

Epileptic seizures are associated with abnormal patterns of neuronal activity and synchronization. Understanding the mechanisms underlying transitions between asynchronous and highly synchronized network states is important for investigating seizure initiation and developing potential predictive biomarkers.

This project examines how periods of reduced neuronal firing may precede synchronization events.

Three quantities are particularly relevant:

| Measurement | Description |
|---|---|
| Mean silence time, `<T>` | Duration-based measure of neuronal inactivity and the proposed biomarker |
| Kuramoto order parameter, `R(t)` | Measure of network phase synchronization |
| Coefficient of variation, `CV(t)` | Characterization of neuronal firing irregularity |

The study also explores the contribution of slow potassium currents to the emergence of seizure-like network dynamics.

## Computational Methods

### Conductance-Based Neuronal Network Simulations

The neuronal model is implemented in C and simulates recurrent network activity.

The simulation component provided in this repository is intended to reproduce **Figure 5(a)** of the publication, rather than every result in the paper.

The model can be used to investigate:

- Spontaneous transitions between different network activity states
- Neuronal firing and population synchronization
- Changes in mean silence time
- Effects of coupling strength and other model parameters
- Relationships between neuronal silence and synchronization

By default, the supplied simulation is configured for 250 seconds of neuronal activity.

### Random Forest Analysis

The Python component implements a Random Forest workflow that uses mean silence time series to predict the Kuramoto synchronization parameter.

The predictive inputs include two time-delayed values of `<T>`, covering a total delay of 10 ms, to estimate a subsequent value of `R(t)`.

The workflow includes model training, prediction on example time series, and performance evaluation.

The repository provides four example mean silence time series for exploring the method.

## Repository Structure

```text
Neuronal-silence-as-an-epileptic-seizure-biomarker/
├── Neuronal model simulation/
│   ├── C simulation source files
│   └── plots.ipynb
├── Random Forest/
│   ├── Python analysis notebooks
│   └── Example time series
└── README.md
```

The file groups above describe their functions; individual source filenames should be checked in the corresponding directories.

## Requirements

### Neuronal Simulations

- A C compiler, such as GCC or Intel's C compiler
- A compatible operating system and sufficient CPU resources

### Machine Learning and Visualization

- Python
- Jupyter Notebook or JupyterLab
- Scientific computing and machine learning libraries required by the supplied notebooks

A reproducible Python environment with exact package versions is recommended.

## How to Run

### 1. Neuronal Network Simulation

Open the `Neuronal model simulation/` directory.

Compile the C program using a compatible compiler, including any required source files and mathematical libraries.

Run the compiled executable from the directory expected by the simulation code.

The exact source-file and executable names should be obtained from the supplied C files before compiling.

The simulation generates numerical output files for subsequent analysis.

**Recommendation:** Start with a shorter simulation to verify compilation, input parameters, and data generation before reproducing longer simulation conditions.

### 2. Simulation Visualization

Open the provided `plots.ipynb` notebook in Jupyter.

The notebook can be used to visualize the recorded network activity and investigate the relationships between neuronal silence, synchronization, and firing irregularity.

### 3. Random Forest Analysis

Navigate to the `Random Forest/` directory.

Open the supplied Python notebook and configure the paths to the example time series.

Run the notebook to train or evaluate the predictive model, visualize its outputs, and explore the influence of mean silence time.

## Analysis and Outputs

The C simulation produces four types of `.dat` output:

| Output | Description |
|---|---|
| Kuramoto order parameter | Time evolution of population synchronization |
| Coefficient of variation | Spike-train irregularity |
| Mean silence time | Time evolution of the proposed biomarker |
| Spike raster data | Individual neuronal spike times |

For reduced output size, the supplied raster output saves spikes from 200 neurons.

The Python notebook supports analysis of prediction quality and visualization of the estimated synchronization dynamics.

## Reproducibility Notes

- The provided C example is associated specifically with Figure 5(a).
- Simulation runtime depends on network parameters and CPU performance.
- The complete research study includes analyses beyond the supplied simulation example.
- Human electrophysiological data analyzed in the paper were originally published by Elahian et al. and can be accessed through [Zenodo](https://doi.org/10.5281/zenodo.836286).
- The proposed biomarker and simulated suppression strategy are research findings, not a clinically validated seizure-prediction or treatment system.
- Prediction performance should be assessed using appropriate validation methods before applying the workflow to new datasets.

## Scientific Reference

Souza, D. L. M., Bentivoglio, L. E., Gabrick, E. C., et al. (2026). **Neuronal silence as a predictive biomarker and target for epileptic seizures suppression.** *Scientific Reports*, 16, 16732.

https://doi.org/10.1038/s41598-026-44063-w
