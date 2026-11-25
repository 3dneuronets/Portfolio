[← Service](../README.md)

# HD-MEA and aging electrophysiology

Research-stage notebooks for spike detection, transfer entropy, network topology and patch-clamp properties.

**Status:** research implementation, release review required.

## Main files

- [`HD_MEA_Analysis/HighDensityMEA_SpikeDetection.ipynb`](HD_MEA_Analysis/HighDensityMEA_SpikeDetection.ipynb)
- [`HD_MEA_Analysis/TransferEntropyGraphAnalysis.ipynb`](HD_MEA_Analysis/TransferEntropyGraphAnalysis.ipynb)
- [`Whole-cell_patch-clamp/ANALISES_ATIVAS_3spikes_after_reo_base.ipynb`](Whole-cell_patch-clamp/ANALISES_ATIVAS_3spikes_after_reo_base.ipynb)
- [`Whole-cell_patch-clamp/ANALISES_PASSIVAS_FxI_VxI.ipynb`](Whole-cell_patch-clamp/ANALISES_PASSIVAS_FxI_VxI.ipynb)

## Environment and usage

Python/Jupyter, HerdingSpikes, pyinform, NetworkX, PyABF, eFEL; partial requirements supplied.

Read the [original technical documentation](README-original.md) for detailed analysis, setup and usage instructions. Notebook outputs have been cleared; original source cells and relative project layout are preserved.

## Important limitations

BRW/ABF recordings not included. The supplied MEA export cell treats `H.spikes` as a filename; adapt the export before graph analysis. Check 7,062 Hz/4,096-channel assumptions, protocol windows and paths. Transfer entropy is directed dependence, not anatomy. Aging project manuscript and results are not supplied.

No execution or numerical reproduction was performed. Check licenses, collaborator permission, sensitive local paths and data rights before release.
