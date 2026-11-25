[← Service](../README.md)

# Whole-cell electrophysiology

ABF current-step and spontaneous-event analysis research workflows.

**Status:** research implementation, release review required.

## Main files

- [`analysis_active_parameters_square_pulses_Freq_I.ipynb`](analysis_active_parameters_square_pulses_Freq_I.ipynb)
- [`analysis_active_parameters_square_pulses_mean3spikes.ipynb`](analysis_active_parameters_square_pulses_mean3spikes.ipynb)
- [`analysis_passive_parameters_square_pulses.ipynb`](analysis_passive_parameters_square_pulses.ipynb)
- [`analysis_spontaneus_activity.ipynb`](analysis_spontaneus_activity.ipynb)

## Environment and usage

Python/Jupyter, PyABF, eFEL, SciPy, NumPy, Pandas, Matplotlib, Seaborn.

Read the [original technical documentation](README-original.md) for detailed analysis, setup and usage instructions. Notebook outputs have been cleared; original source cells and relative project layout are preserved.

## Important limitations

No ABF data supplied. Adapt Google Drive paths, protocols and group labels. `tau_exp` is the absolute exponential rate coefficient, not a validated time constant. No unpublished results or manuscript association asserted.

No execution or numerical reproduction was performed. Check licenses, collaborator permission, sensitive local paths and data rights before release.
