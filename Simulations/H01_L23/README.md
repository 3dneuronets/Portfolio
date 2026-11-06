# Human Cortex Layer 2/3 H01 Model with NetPyNE and CoreNEURON GPU Acceleration

This repository contains an implementation of a **human cortical layer 2/3 (L2/3) network model from H01** developed using **NetPyNE** and adapted to run with **CoreNEURON**, enabling accelerated simulations using GPUs.

The model is based on a detailed biophysical representation of human cortical L2/3 neurons, including morphologically detailed cells, synaptic mechanisms, and network connectivity. The implementation uses the NetPyNE framework for network construction and simulation setup, while CoreNEURON is used as the simulation engine to enable high-performance execution and GPU acceleration.

The EEG forward modeling procedure uses the New York Head Model (sa_nyhead.mat) to calculate scalp potentials from the simulated current dipole moments.


The model can be downloaded directly from the official repository:

https://www.parralab.org/nyhead/sa_nyhead.mat

After downloading, place sa_nyhead.mat in the simulation directory.

Reference:

Huang, Y., Parra, L. C., & Haufe, S. (2016). The New York Head—A precise standardized volume conductor model for EEG source localization and tES targeting. NeuroImage, 140, 150–162. https://doi.org/10.1016/j.neuroimage.2015.12.019



