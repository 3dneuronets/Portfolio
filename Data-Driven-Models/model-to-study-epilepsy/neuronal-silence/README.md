[← Service](../README.md)

# Neuronal silence simulation and prediction

C network implementation targeting Figure 5a and Random Forest estimation of R(t) from silence time series.

**Status:** research implementation, release review required.

## Main files

- [`Neuronal model simulation/Neuronal_model_computing_T_R_CV.c`](Neuronal%20model%20simulation/Neuronal_model_computing_T_R_CV.c)
- [`Neuronal model simulation/plots.ipynb`](Neuronal%20model%20simulation/plots.ipynb)
- [`Random Forest/RF_code.ipynb`](Random%20Forest/RF_code.ipynb)

## Environment and usage

C compiler, Python/Jupyter, NumPy, Pandas, SciPy, scikit-learn, Matplotlib, Seaborn.

Read the [original technical documentation](README-original.md) for detailed analysis, setup and usage instructions. Notebook outputs have been cleared; original source cells and relative project layout are preserved.

## Important limitations

The four simulated CSV time series are retained. H01, human intracranial preprocessing and suppression code are not supplied. Verify compiler and paths; simulation outputs are needed by plots notebook. Not a clinical tool.

No execution or numerical reproduction was performed. Check licenses, collaborator permission, sensitive local paths and data rights before release.
