import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os 
import csv
import time
import re
import pickle as pkl
import seaborn as sns
import matplotlib.colors as mcolors
import warnings

####################### Max Entropy ##########################
##############################################################
def Max_Entropy(x_rand, y_rand, Serie, StatsBlock):
    # --- Configurações Iniciais ---
    Threshold = 0.
    Frac = 10
    Frac2 = 10
    Increase_Thr = 1./Frac
    Max_Threshold = 0.0
    S_Max = 0


    pow_vec = 2 ** np.arange(StatsBlock * StatsBlock).astype(np.int64)
    
    num_samples = len(x_rand)
    pixel_distances = np.zeros((num_samples, StatsBlock * StatsBlock))
    
    for k in range(StatsBlock * StatsBlock):
        dy, dx = divmod(k, StatsBlock) # dy = k // N, dx = k % N

        pixel_distances[:, k] = np.abs(Serie[x_rand + dx] - Serie[y_rand + dy])


    for i in range(Frac2):
        if i > 0:
            Threshold = Max_Threshold - 1.0 * Increase_Thr
            Increase_Thr = ((2.0 * Increase_Thr) / (1.0 * Frac))
        
        for j in range(Frac):

            bool_matrix = pixel_distances <= Threshold
            
            microstate_indices = bool_matrix.dot(pow_vec)

            Stats = np.bincount(microstate_indices, minlength=pow(2, StatsBlock*StatsBlock))
            

            valid_counts = Stats

            nonzero_counts = valid_counts[valid_counts > 0]

            if len(nonzero_counts) > 0:
                total = sum(valid_counts)  #samples #
                probs = nonzero_counts / total #samples
                partials = -probs * np.log(probs)
                S = np.sum(partials)
            else:
                S = 0

            if S > S_Max:
                S_Max = S
                Max_Threshold = Threshold
                StatsM = Stats
            
            Threshold = Threshold + Increase_Thr
            
    return Max_Threshold, S_Max, StatsM

####################### Normalize time series and calculate Max Entropy ##########################
##############################################################
def compute_MaxEntropy(df, StatsBlock=3, samples=50000):

    pow_vec = np.zeros((StatsBlock * StatsBlock), np.int64)
    for K in range(StatsBlock * StatsBlock):
        pow_vec[K] = int(2 ** K)

    out = {}

    Serie = df.values
    Serie = (Serie - np.min(Serie)) / (np.max(Serie) - np.min(Serie))
    Size = len(Serie)

    Stats = np.zeros((2 ** (StatsBlock * StatsBlock)))

    x_rand = np.random.choice(Size - StatsBlock - 1, samples)
    y_rand = np.random.choice(Size - StatsBlock - 1, samples)


    Eps, S_max, Stats = Max_Entropy(x_rand, y_rand, Serie, StatsBlock)

    Smax_norm = S_max / (StatsBlock * StatsBlock * np.log(2))

    out[f'Smax']  = Smax_norm
    out[f'eps']   = Eps
    out[f'Stats'] = Stats

    return out
