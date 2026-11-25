# Whole-Cell Patch-Clamp Analysis

**Intracellular Electrophysiology · Membrane Properties · Action Potentials · Spontaneous Synaptic Events**

## Overview

This repository contains Jupyter notebooks for quantitative analysis of **whole-cell patch-clamp recordings** stored in Axon Binary Format (`.abf`). The analysis code focuses on **intrinsic electrophysiological properties of hippocampal neurons**, their responses to injected-current steps, and detection of spontaneous inward current events.

The example folder organization in the notebooks separates **control (`CONTROLE`) and anoxia (`ANOXIA`) recordings**, including a **P14–P17 hippocampal (`HPC`) dataset**. These are labels and selections found in the code, not independent confirmation of the full experimental protocol or results.

The notebooks combine **PyABF**, **eFEL**, NumPy/SciPy, Pandas, and scientific visualization to support feature extraction, comparison, and inspection of recordings. This repository provides an *analysis workflow*, not raw electrophysiological data or a neural-network simulation model.

> **Research status:** This description is based on the available code. No unpublished conclusions, manuscript title, or quantitative scientific findings are asserted here.

## Repository structure

```text
IC_V_analysis/
├── analysis_active_parameters_square_pulses_Freq_I.ipynb
├── analysis_active_parameters_square_pulses_mean3spikes.ipynb
├── analysis_passive_parameters_square_pulses.ipynb
├── analysis_spontaneus_activity.ipynb
└── README.md
```

## Analysis notebooks

| Notebook | Main purpose |
| --- | --- |
| `analysis_active_parameters_square_pulses_Freq_I.ipynb` | Extract electrophysiological features from current-step recordings and examine responses as a function of injected current, including voltage/current relationships and intrinsic excitability measures. |
| `analysis_active_parameters_square_pulses_mean3spikes.ipynb` | Detect a firing sweep, extract action-potential features with eFEL, and compare measures from the first action potential with averages across the first three action potentials. |
| `analysis_passive_parameters_square_pulses.ipynb` | Characterize passive/subthreshold responses, including voltage deflection, sag, input resistance, and membrane time-constant/capacitance estimates. |
| `analysis_spontaneus_activity.ipynb` | Preprocess intracellular current traces, detect spontaneous negative-going events, and quantify event statistics and waveforms. |

### Active membrane properties

The active-property notebooks read `.abf` recordings with `pyabf`, identify current-step sweeps, and use **eFEL** to extract features including:

- Action-potential amplitude, peak voltage, and width/half-width
- Spike onset and timing measures
- Afterhyperpolarization-related features
- Spike count, firing frequency, and selected interspike-interval statistics

The notebooks support visualization of example traces, tabulation of feature values, and comparisons between the dataset's control and anoxia groups. The `mean3spikes` workflow explicitly calculates summaries of the **first three detected action potentials** for selected measurements and also keeps first-spike values.

### Passive membrane properties

The passive-property workflow uses subthreshold current steps to characterize:

- Baseline and steady-state membrane voltage
- Voltage response to injected current
- Input resistance
- Voltage sag and sag ratio
- Membrane time constant and capacitance estimates

The notebooks also include current–voltage plots, group comparisons, and calculations based on eFEL and direct numerical fitting. Interpretation depends on the selected stimulation windows, current steps, and recording protocols.

### Spontaneous activity and event detection

`analysis_spontaneus_activity.ipynb` implements a separate event-analysis workflow:

1. Read an `.abf` current trace and select a recording interval.
2. Apply baseline adjustment and a low-pass filter.
3. Detect **negative-going events** with `scipy.signal.find_peaks` applied to the inverted trace.
4. Measure event amplitude, inter-event interval, half-height width, area, and rise/decay-related measurements.
5. Fit an exponential function to a post-peak window and generate event plots and `.csv` tables.

The detection thresholds and fitting assumptions are hard-coded for the example recordings; they must be reviewed before reuse. The notebook variable `tau_exp` currently stores the **absolute fitted exponential rate coefficient**, not necessarily the decay time constant itself. Do not interpret that column as a time constant without checking and, if necessary, correcting the calculation.

## Requirements

The code uses **Python 3** and Jupyter notebooks, with several cells designed for **Google Colab**. Packages imported across the notebooks include:

- `pyabf` — reads Axon `.abf` recordings
- `efel` — extracts electrophysiological features
- `numpy`, `scipy`, `pandas` — numerical analysis and tables
- `matplotlib`, `seaborn` — plotting and group visualization
- `IPython` and Jupyter — interactive notebook execution

An initial local environment can be created with:

```bash
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
python -m pip install jupyter numpy scipy pandas matplotlib seaborn pyabf efel
```

The repository does **not** include a pinned `requirements.txt` or a tested cross-platform environment specification. Different eFEL versions may require minor API adjustments.

## How to use

1. **Provide `.abf` recordings.** Raw experimental recordings are **not included** in the repository.
2. **Choose a notebook** according to the analysis: active properties, passive properties, first-three-spike analysis, or spontaneous-event detection.
3. **Update file paths.** Replace the Google Drive paths and recording-folder names with your own accessible paths. The example notebooks assume particular laboratory directory structures and experiment labels.
4. **Check the protocol.** Verify current-step amplitudes, stimulation onset/end times, units, data rate, sampling windows, selection criteria, and event-detection thresholds against the recording metadata.
5. **Run cells in order** in Colab or a compatible local Jupyter environment. Remove or replace Colab-only commands for local use.
6. **Inspect outputs.** The notebooks produce plots, parameter tables, and—where enabled—CSV files. Some output paths are fixed in the code (for example, `Analises_Fernando/`) and must be created or changed before exporting.

**Example workflow:** For current-clamp recordings, begin with `analysis_passive_parameters_square_pulses.ipynb`, then use one of the active-property notebooks. For spontaneous negative-going synaptic-current events, use `analysis_spontaneus_activity.ipynb` as a separate workflow.

## Reproducibility and known limitations

- The notebooks are organized around **specific experimental recordings**, not a generic input-file selection interface.
- Some cells contain hard-coded index selections, recording paths, group names, stimulation windows, example ABF filenames, and filter/event thresholds.
- Certain notebooks mix exploration, parameter extraction, plotting, and statistical comparisons in the same file. Users should verify assumptions and run order before transferring the analyses to another dataset.
- **No raw ABF files or environment lockfile are included.** The code was examined statically; **full execution and reproduction of numerical findings were not verified**.
- The code detects events based on signal characteristics; the underlying synaptic-event identity must be established from the experimental recording conditions, not from this detection routine alone.

## Citation and contact

Please credit this repository if you reuse its analysis workflows and cite the corresponding scientific publication once its reference is publicly available.

*This README documents the computational workflow without disclosing unpublished scientific conclusions.*
