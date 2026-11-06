# Aging and Hippocampal Dysfunction — Electrophysiological Data Analysis

**High-density MEA · Spike detection · Transfer entropy · Network topology · Whole-cell patch clamp**

## Overview

This repository contains Jupyter notebooks for the analysis of electrophysiological recordings used in research on aging and hippocampal dysfunction. It brings together two complementary approaches:

1. **High-density microelectrode array (HD-MEA) analysis**, from extracellular spike detection to directed statistical-dependence networks based on transfer entropy.
2. **Whole-cell patch-clamp analysis**, for characterizing passive membrane properties and action-potential features from intracellular recordings.

The code demonstrates workflows for processing neural recordings, extracting quantitative features, visualizing activity, and comparing experimental groups. **This is an analysis-code repository, not a released dataset.**

> **Research status:** This README describes the methods visible in the public code. It does not present unpublished study conclusions. Add the manuscript reference and approved scientific summary when they can be shared.

## Repository structure

```text
Aging_and_Hippocampal_Dysfunction/
├── HD_MEA_Analysis/
│   ├── HighDensityMEA_SpikeDetection.ipynb
│   └── TransferEntropyGraphAnalysis.ipynb
├── Whole-cell_patch-clamp/
│   ├── ANALISES_ATIVAS_3spikes_after_reo_base.ipynb
│   └── ANALISES_PASSIVAS_FxI_VxI.ipynb
├── requirements.txt
└── README.md
```

## Analysis workflows

### 1. HD-MEA spike detection

**Notebook:** [`HD_MEA_Analysis/HighDensityMEA_SpikeDetection.ipynb`](HD_MEA_Analysis/HighDensityMEA_SpikeDetection.ipynb)

- Reads `.brw` recordings through the `BioCam` interface in **HerdingSpikes**.
- Inspects recording noise across channels and supports manual channel masking.
- Runs spike detection/localization with `HSDetection`.
- Displays detected activity as a channel-by-time raster plot and inspects event waveforms.
- Contains a step intended to export a spike table for subsequent analysis.

The example notebook assumes a 4,096-channel recording and uses a recording-specific sampling rate of **7,062 Hz** in its raster/analysis steps. Verify both against your dataset before reusing the parameters.

### 2. Transfer entropy and graph analysis

**Notebook:** [`HD_MEA_Analysis/TransferEntropyGraphAnalysis.ipynb`](HD_MEA_Analysis/TransferEntropyGraphAnalysis.ipynb)

- Imports a spike-event table with channel and sample-time information.
- Constructs a binary channel-by-time spike matrix, rebins it from 7,062 Hz to 1,000 Hz, and excludes inactive channels.
- Estimates **pairwise directed transfer entropy** using `pyinform`.
- Uses circularly shifted surrogate spike trains to estimate empirical significance; also applies false-discovery-rate (FDR) correction.
- Builds a directed, weighted graph using `NetworkX` and evaluates graph properties, including density, degree, clustering, shortest paths, modularity, and eigenvector centrality.
- Compares graph metrics against random-network null models and reports standardized differences.

The notebook currently requests **300 surrogates per ordered channel pair** and **2,000 random networks**. Pairwise analysis scales rapidly with the number of active channels and can require substantial memory and CPU time. **Transfer entropy quantifies directed statistical dependence; it does not by itself establish anatomical or causal synaptic connectivity.**

### 3. Active membrane properties

**Notebook:** [`Whole-cell_patch-clamp/ANALISES_ATIVAS_3spikes_after_reo_base.ipynb`](Whole-cell_patch-clamp/ANALISES_ATIVAS_3spikes_after_reo_base.ipynb)

- Reads `.abf` files using `pyabf` and selects current-step recordings.
- Identifies a depolarizing sweep producing at least three spikes, near the cell's firing threshold in the implemented sweep search.
- Extracts features with **eFEL**, including action-potential amplitude, width, afterhyperpolarization, spike timing, and firing statistics.
- Computes summaries over the initial three action potentials where supported by the selected feature.
- Generates group comparisons, plots, and tabular exports.

### 4. Passive membrane properties and current–voltage responses

**Notebook:** [`Whole-cell_patch-clamp/ANALISES_PASSIVAS_FxI_VxI.ipynb`](Whole-cell_patch-clamp/ANALISES_PASSIVAS_FxI_VxI.ipynb)

- Measures resting/baseline voltage, voltage deflection, sag amplitude and ratio, and membrane time-constant-related quantities.
- Estimates input resistance and membrane capacitance from responses to injected current, subject to the assumptions in the notebook.
- Inspects current–voltage responses and related firing properties.
- Produces plots, group comparisons, and `.xlsx` result tables.

The patch-clamp notebooks contain folder and group labels for **SAMP8 recordings at approximately 2 months (`SAMP2`) and 7–8 months (`SAMP8`)**, including a **caffeine-associated condition (`SAMP8-Caf`)**. Those names reflect the analysis code; interpretation of the experimental design should follow the associated study protocol.

## Requirements

Most notebooks were written for **Google Colab** and use Google Drive for accessing source recordings. The repository contains a partial `requirements.txt` specifying versions of NumPy, Pandas, SciPy, Seaborn, IPython, and related packages. Additional libraries imported by the notebooks include:

- `herdingspikes` (the spike-detection notebook requests `herdingspikes==0.3.100`)
- `pyinform`, `networkx`, `statsmodels`, `joblib`, `tqdm`
- `pyabf`, `efel`, `matplotlib`, `scikit-learn`
- An Excel writer such as `openpyxl` for `.xlsx` output

For a local Jupyter environment, an initial setup is:

```bash
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install jupyter matplotlib pyabf efel scikit-learn \
    networkx pyinform statsmodels joblib tqdm openpyxl
```

For HD-MEA spike detection, additionally install a **compatible HerdingSpikes version**; the notebook contains its original Colab installation command. Compatibility between older pinned packages, HerdingSpikes, the Python version, and the operating system has **not** been validated here.

## How to use

1. **Obtain your recordings.** The original `.brw` and `.abf` files are **not included** in this repository. Use your own authorized recordings or obtain access from the study team.
2. **Configure paths and groups.** Open the relevant notebook and replace Google Drive paths, study-specific folder names, and experimental-group selections with the locations of your data. For local Jupyter use, remove or replace the Colab-specific Drive-mounting and shell commands.
3. **HD-MEA workflow:** Run `HighDensityMEA_SpikeDetection.ipynb` with the correct `.brw` file and detector settings; verify the spike-table export before feeding it to `TransferEntropyGraphAnalysis.ipynb`.
4. **Patch-clamp workflow:** Run the active or passive notebook with matching `.abf` recordings and stimulation protocols; check current-step timing, sampling rates, units, and group assignments.
5. **Review results.** Confirm detected spikes/events visually and inspect generated rasters, waveforms, plots, and CSV/Excel tables before drawing scientific conclusions.

**Important:** The MEA export cell in the supplied notebook attempts `pd.read_csv('H.spikes', ...)`, which is a literal filename rather than an automatic conversion from the in-memory `H.spikes` object. This step requires correction or adaptation to the actual HerdingSpikes output format before the transfer-entropy notebook can use the CSV.

## Reproducibility and limitations

- **Input data are absent** from the repository. Several notebooks rely on laboratory-specific Drive paths, manually chosen channel masks, hard-coded protocol assumptions, and recording-specific sample rates.
- The current notebooks are research workflows, not a single automated command-line pipeline. Some cells assume earlier interactive state or specific example recordings.
- The transfer-entropy analysis can consume substantial memory because it first constructs a dense binary matrix at the original sample rate, and it evaluates all ordered pairs of active channels.
- The included `requirements.txt` is **not a complete environment specification** for all four notebooks.
- Source code was reviewed statically for this documentation; **end-to-end execution and numerical reproduction were not verified** without the original recordings.

## Citation and contact

If you use the analysis code in research, please credit the repository and the associated publication when a citation becomes available.

*This README describes the available code and intentionally does not disclose unpublished results.*
