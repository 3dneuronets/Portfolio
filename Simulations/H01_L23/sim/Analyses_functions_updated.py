import numpy as np


# =============================================================================
# Helper functions
# =============================================================================

def _make_spike_dict(spkt, spkid, gids):
    """
    Convert NetPyNE spkt/spkid arrays into

        spikes[gid] = np.array([t1, t2, t3, ...])

    Spike times are in ms.
    """

    spkt = np.asarray(spkt, dtype=float)
    spkid = np.asarray(spkid, dtype=int)

    gid_set = set(int(gid) for gid in gids)

    spikes = {
        int(gid): []
        for gid in gids
    }

    for t, gid in zip(spkt, spkid):
        gid = int(gid)

        if gid in gid_set:
            spikes[gid].append(float(t))

    for gid in spikes:
        spikes[gid] = np.asarray(
            spikes[gid],
            dtype=float
        )

    return spikes


# =============================================================================
# Per-neuron firing rate and ISI coefficient of variation
# =============================================================================

def compute_spike_stats(
    spkt,
    spkid,
    gids,
    transient=0.0,
    tstop=None,
    min_spikes_cv=3,
):
    """Summarize per-neuron firing rates and ISI CVs for one neuron group.

    Analysis interval: transient < spike_time <= tstop (times in ms).
    Rate: number of spikes in the interval / interval duration in seconds.
    CV: std(ISIs) / mean(ISIs) computed for each neuron separately.

    Silent neurons contribute 0 Hz to firing-rate statistics. A neuron with
    fewer than ``min_spikes_cv`` spikes has undefined CV (NaN); its CV is not
    included in the group CV statistics.

    The standard deviations of both ISIs and cell-level population metrics
    use ddof=0 (population SD).
    """
    if tstop is None or tstop <= transient:
        raise ValueError("tstop must be specified and greater than transient")
    if min_spikes_cv < 3:
        raise ValueError("min_spikes_cv must be at least 3 (two ISIs)")

    gids = np.asarray(list(gids), dtype=int)
    if len(np.unique(gids)) != len(gids):
        raise ValueError("gids contains duplicate neuron IDs")
    if len(spkt) != len(spkid):
        raise ValueError("spkt and spkid must have equal lengths")

    spikes = _make_spike_dict(spkt, spkid, gids)
    duration_s = (float(tstop) - float(transient)) / 1000.0

    rates = np.zeros(len(gids), dtype=float)
    cvs = np.full(len(gids), np.nan, dtype=float)
    n_spikes = np.zeros(len(gids), dtype=int)

    for i, gid in enumerate(gids):
        times = spikes[int(gid)]
        times = np.sort(times[(times > transient) & (times <= tstop)])

        n_spikes[i] = len(times)
        rates[i] = len(times) / duration_s

        if len(times) >= min_spikes_cv:
            isis = np.diff(times)
            if np.all(isis > 0):
                cvs[i] = float(np.std(isis, ddof=0) / np.mean(isis))

    valid_cv = cvs[np.isfinite(cvs)]

    def describe(values):
        if len(values) == 0:
            return float('nan'), float('nan'), float('nan')
        return (
            float(np.mean(values)),
            float(np.median(values)),
            float(np.std(values, ddof=0)),
        )

    rate_mean, rate_median, rate_std = describe(rates)
    cv_mean, cv_median, cv_std = describe(valid_cv)

    return {
        'rateMeanHz': rate_mean,
        'rateMedianHz': rate_median,
        'rateStdHz': rate_std,
        'CVMean': cv_mean,
        'CVMedian': cv_median,
        'CVStd': cv_std,
        'CV': cv_mean,  # compatibility: old ['CV'] is now the mean of cell CVs
        'nCells': int(len(gids)),
        'nSpikingCells': int(np.count_nonzero(n_spikes)),
        'nCVCells': int(len(valid_cv)),
        # One-to-one per-neuron arrays (all have the same ordering):
        'gids': gids,
        'rateHzPerNeuron': rates,
        'CVperNeuron': cvs,
        'nSpikesPerNeuron': n_spikes,
    }


def compute_network_spike_stats(
    spkt,
    spkid,
    pop_gids,
    transient=0.0,
    tstop=None,
    min_spikes_cv=3,
):
    """Report per-neuron firing rate/CV summaries for network populations."""
    populations = {
        pop: list(gids)
        for pop, gids in pop_gids.items()
    }

    all_gids = [gid for gids in populations.values() for gid in gids]
    exc = list(populations.get('HL23PYR', []))
    inh = [
        gid
        for pop in ('HL23SST', 'HL23PV', 'HL23VIP')
        for gid in populations.get(pop, [])
    ]

    if len(set(all_gids)) != len(all_gids):
        raise ValueError('Neuron GIDs overlap between populations')

    groups = {'all': all_gids, 'exc': exc, 'inh': inh}
    groups.update(populations)

    return {
        group: compute_spike_stats(
            spkt=spkt,
            spkid=spkid,
            gids=gids,
            transient=transient,
            tstop=tstop,
            min_spikes_cv=min_spikes_cv,
        )
        for group, gids in groups.items()
    }


def compute_cv(spkt, spkid, gids, transient=0.0, tstop=None):
    """Backward-compatible entry point; CV now means mean per-neuron CV."""
    return compute_spike_stats(spkt, spkid, gids, transient, tstop)


def compute_network_cv(spkt, spkid, pop_gids, transient=0.0, tstop=None):
    """Backward-compatible entry point; includes per-neuron rate/CV stats."""
    return compute_network_spike_stats(spkt, spkid, pop_gids, transient, tstop)


def compute_frequency_cv(spkt, spkid, gids, transient=0.0, tstop=None):
    """For the existing compute_network_metrics() helper in this file."""
    return compute_spike_stats(spkt, spkid, gids, transient, tstop)

# =============================================================================
# Kuramoto order parameter
# =============================================================================
def compute_network_kuramoto(
    spkt,
    spkid,
    pop_gids,
    transient,
    tstop,
    sample_step,
    return_time_series=False,
):

    pyr_gids = list(pop_gids['HL23PYR'])
    sst_gids = list(pop_gids['HL23SST'])
    pv_gids  = list(pop_gids['HL23PV'])
    vip_gids = list(pop_gids['HL23VIP'])

    exc_gids = pyr_gids

    inh_gids = (
        sst_gids
        + pv_gids
        + vip_gids
    )

    all_gids = (
        exc_gids
        + inh_gids
    )

    groups = {
        'all': all_gids,
        'exc': exc_gids,
        'inh': inh_gids,

        'HL23PYR': pyr_gids,
        'HL23SST': sst_gids,
        'HL23PV': pv_gids,
        'HL23VIP': vip_gids,
    }

    # -------------------------------------------------------------------------
    # Global kinitial
    #
    # Match original C implementation:
    # kinitial is the first spike after transient anywhere in the network.
    # -------------------------------------------------------------------------

    spkt_array = np.asarray(
        spkt,
        dtype=float
    )

    spkid_array = np.asarray(
        spkid,
        dtype=int
    )

    all_gid_set = set(all_gids)

    mask = np.array(
        [
            gid in all_gid_set
            for gid in spkid_array
        ],
        dtype=bool
    )

    network_spikes = spkt_array[
        mask
        &
        (spkt_array > transient)
        &
        (spkt_array <= tstop)
    ]

    if len(network_spikes) > 0:
        global_kinitial = float(
            np.min(network_spikes)
        )
    else:
        global_kinitial = None

    # -------------------------------------------------------------------------
    # Calculate Kuramoto for every group
    # -------------------------------------------------------------------------

    results = {}

    for group_name, gids in groups.items():

        results[group_name] = compute_kuramoto(
            spkt=spkt,
            spkid=spkid,
            gids=gids,
            transient=transient,
            tstop=tstop,
            sample_step=sample_step,
            global_kinitial=global_kinitial,
            return_time_series=return_time_series,
        )

    return results



def compute_kuramoto(
    spkt,
    spkid,
    gids,
    transient,
    tstop,
    sample_step,
    global_kinitial=None,
    return_time_series=False,
):
    """
    Kuramoto order parameter calculated from spike phases.

    This follows Compute_Kuramoto_Order_Parameter()
    from the original C implementation.

    Only neurons with at least two spikes after the transient
    contribute to R(t).
    """

    spikes = _make_spike_dict(
        spkt,
        spkid,
        gids
    )

    # -------------------------------------------------------------------------
    # Keep only post-transient spikes for Kuramoto
    #
    # This corresponds to:
    #
    # if(time > transient)
    #     nk[k[i]][i] = time;
    # -------------------------------------------------------------------------

    valid_spikes = {}

    for gid, times in spikes.items():

        times = times[
            (times > transient)
            &
            (times <= tstop)
        ]

        if len(times) >= 2:
            valid_spikes[gid] = times

    if len(valid_spikes) == 0:

        result = {
            'Rmean': 0.0,
            'nCells': 0,
            'kinitial': np.nan,
            'kfinal': np.nan,
        }

        if return_time_series:
            result['time'] = np.array([])
            result['R'] = np.array([])

        return result

    # -------------------------------------------------------------------------
    # kinicial
    #
    # The C program uses the first post-transient spike occurring anywhere
    # in the complete network.
    # -------------------------------------------------------------------------

    if global_kinitial is None:

        kinitial = min(
            times[0]
            for times in valid_spikes.values()
        )

    else:

        kinitial = float(global_kinitial)

    # -------------------------------------------------------------------------
    # kfinal
    #
    # Original C code finds the earliest LAST spike among neurons with >=2
    # spikes.
    #
    # Therefore every neuron still has an interval surrounding each time
    # used in the average.
    # -------------------------------------------------------------------------

    kfinal = min(
        times[-1]
        for times in valid_spikes.values()
    )

    if kfinal <= kinitial:

        result = {
            'Rmean': 0.0,
            'nCells': len(valid_spikes),
            'kinitial': float(kinitial),
            'kfinal': float(kfinal),
        }

        if return_time_series:
            result['time'] = np.array([])
            result['R'] = np.array([])

        return result

    # Equivalent to:
    #
    # for(time=transient; time<=...; time=time+2*step)
    #
    times_eval = np.arange(
        kinitial,
        kfinal + sample_step * 0.5,
        sample_step,
    )

    n_cells = len(valid_spikes)

    real = np.zeros(
        len(times_eval),
        dtype=float
    )

    imag = np.zeros(
        len(times_eval),
        dtype=float
    )

    # -------------------------------------------------------------------------
    # Calculate phase of every neuron
    # -------------------------------------------------------------------------

    for spike_times in valid_spikes.values():

        phi = np.zeros(
            len(times_eval),
            dtype=float
        )

        # index of spike immediately before time t
        indices = (
            np.searchsorted(
                spike_times,
                times_eval,
                side='right'
            )
            - 1
        )

        valid = (
            (indices >= 0)
            &
            (indices < len(spike_times) - 1)
        )

        idx = indices[valid]

        t0 = spike_times[idx]
        t1 = spike_times[idx + 1]

        phi[valid] = (
            2.0
            * np.pi
            * (times_eval[valid] - t0)
            / (t1 - t0)
        )

        real += np.cos(phi)
        imag += np.sin(phi)

    real /= n_cells
    imag /= n_cells

    R = np.sqrt(
        real ** 2
        +
        imag ** 2
    )

    Rmean = np.mean(R)

    result = {
        'Rmean': float(Rmean),
        'nCells': int(n_cells),
        'kinitial': float(kinitial),
        'kfinal': float(kfinal),
    }

    if return_time_series:

        result['time'] = times_eval
        result['R'] = R

    return result


# =============================================================================
# Complete NetPyNE network analysis
# =============================================================================

def compute_network_metrics(
    spkt,
    spkid,
    pop_gids,
    transient,
    duration,
    dt,
    return_kuramoto_time_series=False,
):
    """
    Calculate the C-equivalent metrics for:

        all
        excitatory
        inhibitory

    and additionally for each NetPyNE population.
    """

    # -------------------------------------------------------------------------
    # Population definitions
    # -------------------------------------------------------------------------

    pyr = list(
        pop_gids.get(
            'HL23PYR',
            []
        )
    )

    sst = list(
        pop_gids.get(
            'HL23SST',
            []
        )
    )

    pv = list(
        pop_gids.get(
            'HL23PV',
            []
        )
    )

    vip = list(
        pop_gids.get(
            'HL23VIP',
            []
        )
    )

    exc = pyr
    inh = sst + pv + vip
    all_gids = exc + inh

    groups = {
        'all': all_gids,
        'exc': exc,
        'inh': inh,
        'PYR': pyr,
        'SST': sst,
        'PV': pv,
        'VIP': vip,
    }

    # -------------------------------------------------------------------------
    # Same global kinicial used by the C program
    # -------------------------------------------------------------------------

    spkt_array = np.asarray(
        spkt,
        dtype=float
    )

    post_transient_spikes = spkt_array[
        (spkt_array > transient)
        &
        (spkt_array <= duration)
    ]

    if len(post_transient_spikes) > 0:
        global_kinitial = float(
            np.min(
                post_transient_spikes
            )
        )
    else:
        global_kinitial = None

    # C:
    #
    # time = time + 2.0 * step
    #
    # therefore use 2*dt here.

    kuramoto_step = 2.0 * dt

    results = {}

    for group_name, gids in groups.items():

        frequency_cv = compute_frequency_cv(
            spkt=spkt,
            spkid=spkid,
            gids=gids,
            transient=transient,
            tstop=duration,
        )

        kuramoto = compute_kuramoto(
            spkt=spkt,
            spkid=spkid,
            gids=gids,
            transient=transient,
            tstop=duration,
            sample_step=kuramoto_step,
            global_kinitial=global_kinitial,
            return_time_series=return_kuramoto_time_series,
        )

        results[group_name] = {
            **frequency_cv,
            **kuramoto,
        }

    return results

def delete_lfp_h5(cfg, sim):

    if (cfg.coreneuron and cfg.recordLFP and hasattr(sim, '_coreLFP_output_dir')):

        import shutil
        import os

        if os.path.isdir(sim._coreLFP_output_dir):

            shutil.rmtree(
                sim._coreLFP_output_dir
            )

            print(
                '[CoreLFP] Deleted temporary folder:',
                sim._coreLFP_output_dir
            )

def delete_dipole_h5(cfg, sim):

    if (cfg.coreneuron and cfg.recordDipole and hasattr(sim,'_coreDipole_output_dir')):

        import shutil
        import os

        if os.path.isdir(sim._coreDipole_output_dir):

            shutil.rmtree(sim._coreDipole_output_dir)

            print(
                '[CoreDipole] Deleted temporary folder:',
                sim._coreDipole_output_dir
            )