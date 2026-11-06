"""Publication/presentation panels for a NetPyNE L2/3 simulation + NYHead EEG.

Requires numpy, scipy, matplotlib, and an initialized lfpykit NYHeadModel.
Uses data['dipoleSum'] in nA*um, simConfig times in milliseconds.
No hard-coded cell counts, GIDs, or electrode indices.

Example is provided in the accompanying response.
"""
from __future__ import annotations

import warnings
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.transforms import blended_transform_factory
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.signal import butter, sosfiltfilt, resample_poly, welch
from fractions import Fraction

COLORS = {
    'HL23PYR': '#D55E00',
    'HL23SST': '#0072B2',
    'HL23PV': '#009E73',
    'HL23VIP': '#CC79A7',
}
NAMES = {p: p.replace('HL23', '') for p in COLORS}
VOLT_ORDER = ['HL23VIP', 'HL23PV', 'HL23SST', 'HL23PYR']
RASTER_ORDER = ['HL23PYR', 'HL23SST', 'HL23PV', 'HL23VIP']
EEG_COLOR = '#26456E'


def figure_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
        'axes.linewidth': 0.8,
        'axes.labelsize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'savefig.dpi': 300,
    })


def _config_value(config, key):
    try:
        return config[key]
    except (KeyError, TypeError):
        return getattr(config, key)


def population_gids(config):
    """Population GIDs from saved simConfig (works for 1,000/1,250 cells)."""
    try:
        starts = _config_value(config, 'cellNumber0')
        counts = _config_value(config, 'cellNumber')
        return {p: np.arange(int(starts[p]), int(starts[p]) + int(counts[p]), dtype=int)
                for p in RASTER_ORDER}
    except (AttributeError, KeyError, TypeError) as exc:
        raise ValueError('Pass a saved simConfig with cellNumber and cellNumber0, '
                         'or supply pop_gids explicitly.') from exc


def _time_vector_ms(data, config, n_samples, label):
    dt_ms = float(_config_value(config, 'recordDipoleStep'))
    if not np.isfinite(dt_ms) or dt_ms <= 0:
        raise ValueError('Invalid cfg.recordStep')
    if 't' in data:
        recorded_t = np.asarray(data['t'], dtype=float)
        if recorded_t.ndim == 1 and len(recorded_t) == n_samples:
            return recorded_t
    t = np.arange(n_samples, dtype=float) * dt_ms
    duration = float(_config_value(config, 'duration'))
    if t[-1] > duration + 1.5 * dt_ms:
        warnings.warn(f'{label}: inferred timestamps extend beyond cfg.duration; '
                      'check sampling rate and whether these files belong to the same run.')
    return t


def select_electrodes(nyhead, n=4, method='distance', dipole_orientation=None,
                      min_separation_mm=25.0):
    """Return electrode indices (0-based), distances (mm), sensitivity scores.

    method='distance': rank by Euclidean cortical-source-to-scalp-contact distance.
    method='normal_gain': rank by abs(M @ cortical surface normal) for
                         a unit dipole normal to this cortical vertex.
    method='model_gain': rank by ||M|| row norm, independent of orientation.
    method='spaced_nearby': closest scalp contacts, keeping approximately
                            min_separation_mm spacing between selected contacts.
    """
    if getattr(nyhead, 'dipole_pos', None) is None:
        raise ValueError('Call nyhead.set_dipole_pos(...) first')
    elecs = np.asarray(nyhead.elecs, dtype=float)
    if elecs.shape[0] < 3:
        raise ValueError('Expected nyhead.elecs with (3, N) coordinates')
    source = np.asarray(nyhead.dipole_pos, dtype=float).reshape(3)
    dists = np.linalg.norm(elecs[:3, :].T - source, axis=1)
    M = np.asarray(nyhead.get_transformation_matrix(), dtype=float)
    if M.shape != (len(dists), 3):
        raise ValueError(f'Lead-field shape {M.shape} not compatible with coordinates')

    normal = np.asarray(nyhead.cortex_normal_vec, dtype=float).reshape(3)
    normal = normal / np.linalg.norm(normal)
    if dipole_orientation is not None:
        normal = np.asarray(dipole_orientation, dtype=float).reshape(3)
        normal /= np.linalg.norm(normal)
    gains = np.abs(M @ normal)
    if method == 'distance':
        ordered = np.argsort(dists, kind='stable')
    elif method == 'normal_gain':
        ordered = np.argsort(-gains, kind='stable')
    elif method == 'model_gain':
        ordered = np.argsort(-np.linalg.norm(M, axis=1), kind='stable')
    elif method == 'spaced_nearby':
        nearest = np.argsort(dists, kind='stable')
        chosen = []
        for ix in nearest:
            pos = elecs[:3, ix]
            if not chosen or all(np.linalg.norm(pos-elecs[:3, prev]) >= min_separation_mm
                                 for prev in chosen):
                chosen.append(int(ix))
            if len(chosen) >= n:
                break
        # Use nearest remaining contacts if this separation is too restrictive.
        ordered = np.asarray(chosen + [int(ix) for ix in nearest if int(ix) not in chosen],
                             dtype=int)
    else:
        raise ValueError('method must be distance, spaced_nearby, normal_gain, or model_gain')
    selected = ordered[:n].astype(int)
    return selected, dists[selected], gains[selected]


def construct_eeg(data, config, nyhead, electrode_ids=None,
                  model_surface_axis=(0., 1., 0.)):
    """Project all or selected channels. Returns EEG in microvolts, time in ms.

    Assumes data['dipoleSum'] is the total current dipole in nA*um (T,3),
    not an already rotated/head-coordinate dipole. A single point equivalent
    dipole is used; no spatially distributed EEG sources are resolved.
    """
    P = np.asarray(data['dipoleSum'], dtype=float)
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("data['dipoleSum'] must have shape (time,3)")
    if not np.all(np.isfinite(P)):
        raise ValueError('Non-finite dipole values')
    axis = np.asarray(model_surface_axis, dtype=float).copy()
    if np.linalg.norm(axis) < 1e-10:
        raise ValueError('Model surface axis cannot be zero')
    # This rotation applies to all 3 components; it is not a projection
    # exclusively onto the surface normal.
    p_head = np.asarray(nyhead.rotate_dipole_to_surface_normal(P.T, orig_ax_vec=axis))
    M = np.asarray(nyhead.get_transformation_matrix(), dtype=float)
    if electrode_ids is not None:
        M = M[np.asarray(electrode_ids, dtype=int)]
    eeg_uV = 1000. * (M @ p_head)  # nA*um -> mV -> uV
    t_ms = _time_vector_ms(data, config, len(P), 'Dipole')
    return eeg_uV, t_ms


def _zero_phase_eeg(x_uV, fs_hz, band_hz=(0.5, 200.0), order=3):
    x = np.asarray(x_uV, dtype=float)
    if band_hz is None:
        return x
    low, high = map(float, band_hz)
    if not (0 < low < high < fs_hz / 2):
        raise ValueError(f'band_hz={band_hz} invalid for fs={fs_hz:g} Hz')
    sos = butter(order, (low, high), btype='bandpass', fs=fs_hz, output='sos')
    return sosfiltfilt(sos, x, axis=-1)


def preprocess_eeg_for_plot(eeg_uV, time_ms, band_hz=(0.5, 200), plot_fs_hz=1000):
    """Zero-phase filter first, then anti-aliased polyphase resampling."""
    t = np.asarray(time_ms, dtype=float)
    if len(t) < 4 or not np.all(np.diff(t) > 0):
        raise ValueError('EEG time vector must be strictly increasing')
    dt_ms = np.median(np.diff(t))
    if not np.allclose(np.diff(t), dt_ms, rtol=1e-4, atol=1e-7):
        raise ValueError('Non-uniform EEG time vector')
    fs = 1000. / dt_ms
    filtered = _zero_phase_eeg(eeg_uV, fs, band_hz=band_hz)
    if plot_fs_hz is None or plot_fs_hz >= fs:
        return t, filtered
    ratio = Fraction(float(plot_fs_hz / fs)).limit_denominator(100000)
    new_x = resample_poly(filtered, ratio.numerator, ratio.denominator, axis=-1)
    fs_actual = fs * ratio.numerator / ratio.denominator
    new_t = t[0] + np.arange(new_x.shape[-1]) * (1000. / fs_actual)
    return new_t, new_x


def _hide_axis(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, right=False, bottom=False,
                   labelbottom=False, labelleft=False)


def _nice_scale(x):
    if x <= 0 or not np.isfinite(x):
        return 1.0
    magnitude = 10 ** np.floor(np.log10(x))
    v = x / magnitude
    return (1 if v < 1.5 else 2 if v < 3.5 else 5 if v < 7.5 else 10) * magnitude


def _format_uv(v):
    if abs(v) >= 0.01:
        return f'{v:g} µV'
    if abs(v) >= 1e-5:
        return f'{v * 1e3:g} nV'
    return f'{v * 1e6:g} pV'


def _vertical_scalebar(ax, magnitude, text, x_frac=-0.009, y_frac=0.1, fontsize=9):
    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()
    x = x1 + x_frac * (x2 - x1)
    y = y1 + y_frac * (y2 - y1)
    ax.plot([x, x], [y, y + magnitude], color='black', lw=1.3, clip_on=False)
    ax.text(x - 0.007 * (x2-x1), y + magnitude/2, text, ha='right', va='center',
            rotation=90, fontsize=fontsize, clip_on=False)


def plot_network_eeg_panel(data, config, eeg_uV, eeg_time_ms, electrode_ids,
                           transient_s=1., start_s=0., stop_s=4.,
                           pop_gids=None, trace_gids=None,
                           filter_band_hz=(0.5, 200.), plot_fs_hz=1000.,
                           figsize=(14, 11), save_prefix=None):
    """4 colored somatic traces, grouped raster, and 4 aligned EEG channels.

    start_s/stop_s are relative to the END of transient_s. All axes share time.
    EEG rows preserve physical signal amplitude ratios (common vertical scale).
    """
    figure_style()
    eeg = np.asarray(eeg_uV, dtype=float)
    elec = np.asarray(electrode_ids, dtype=int)
    if eeg.ndim != 2 or eeg.shape[0] != len(elec):
        raise ValueError('Pass only selected EEG channels: shape (n_selected, n_times)')
    if len(elec) != 4:
        raise ValueError('Figure design currently expects exactly four electrodes')
    if pop_gids is None:
        pop_gids = population_gids(config)
    pop_gids = {p: np.sort(np.asarray(pop_gids[p], dtype=int)) for p in RASTER_ORDER}
    if trace_gids is None:
        recorded = set()
        for key in data['V_soma']:
            if key.startswith('cell_'):
                try:
                    recorded.add(int(key[5:]))
                except ValueError:
                    pass
        trace_gids = {}
        for p in RASTER_ORDER:
            available = np.intersect1d(pop_gids[p], list(recorded))
            if len(available) == 0:
                raise KeyError(f'No recorded V_soma trace for {p}; recorded={recorded}')
            trace_gids[p] = int(available[0])
    t0 = 1000. * (transient_s + start_s)
    t1 = 1000. * (transient_s + stop_s)
    if not (t0 >= 0 and t1 > t0):
        raise ValueError('Invalid plot interval')
    t_eeg = np.asarray(eeg_time_ms, dtype=float)
    t_volt = _time_vector_ms(data, config,
                             len(np.asarray(data['V_soma'][f'cell_{trace_gids[RASTER_ORDER[0]]}'])),
                             'Voltage')
    if t1 > min(t_eeg[-1], t_volt[-1]) + 1e-7:
        raise ValueError(f'Requested display ending at {t1/1000:g} s exceeds '
                         f'recorded signal duration EEG={t_eeg[-1]/1000:g} s, '
                         f'voltage={t_volt[-1]/1000:g} s')
    plot_eeg_t, plot_eeg = preprocess_eeg_for_plot(
        eeg, t_eeg, band_hz=filter_band_hz, plot_fs_hz=plot_fs_hz)
    me = (plot_eeg_t >= t0) & (plot_eeg_t <= t1)
    mv = (t_volt >= t0) & (t_volt <= t1)
    if not np.any(me) or not np.any(mv):
        raise ValueError('No data in time window')

    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(9, 1, figure=fig,
                           height_ratios=[0.52]*4 + [3.8] + [0.63]*4,
                           hspace=0.08,
                           left=0.11, right=0.89, top=0.975, bottom=0.075)
    axs = [fig.add_subplot(gs[i]) for i in range(9)]
    ax0 = axs[0]
    for ax in axs[1:]:
        ax.sharex(ax0)
    xlims = (start_s, stop_s)
    # Cell trace panels
    for i, pop in enumerate(VOLT_ORDER):
        ax = axs[i]
        voltage = np.asarray(data['V_soma'][f'cell_{trace_gids[pop]}'], dtype=float)
        if len(voltage) != len(t_volt):
            raise ValueError('Recorded voltage traces have inconsistent lengths')
        ax.plot((t_volt[mv]-1000*transient_s)/1000., voltage[mv],
                c=COLORS[pop], lw=1.15, clip_on=True)
        ax.set_ylim(-100, 55)
        _hide_axis(ax)
        ax.text(1.008, 0.5, NAMES[pop], transform=ax.transAxes,
                color=COLORS[pop], ha='left', va='center', fontsize=17, clip_on=False)
    axs[3].set_xlim(xlims)
    _vertical_scalebar(axs[3], 100, '100 mV', x_frac=-0.012, fontsize=8)
    # Raster with one strip per population (actual GID ranges; not hardcoded)
    raster_ax = axs[4]
    spikes_t = np.asarray(data['spkt'], dtype=float)
    spikes_g = np.asarray(data['spkid'], dtype=int)
    ms = (spikes_t >= t0) & (spikes_t <= t1)
    spkt = spikes_t[ms]
    spgid = spikes_g[ms]
    vertical_gap = max(12, round(sum(map(len, pop_gids.values())) * 0.008))
    offset = 0
    for i, pop in enumerate(RASTER_ORDER):
        gids = pop_gids[pop]
        mask = np.isin(spgid, gids)
        ranks = np.searchsorted(gids, spgid[mask])
        y = offset + ranks
        raster_ax.scatter((spkt[mask] - transient_s*1000.)/1000., y, s=2, marker='o', c=COLORS[pop], rasterized=True)
        raster_ax.text(-0.018, offset + (len(gids)-1)/2., NAMES[pop], transform=raster_ax.get_yaxis_transform(), ha='right', va='center', fontsize=14, clip_on=False)
        offset += len(gids)
        if i < 3:
            raster_ax.axhline(offset + vertical_gap/2 - 1,
                              c='0.8', lw=0.65)
            offset += vertical_gap
    raster_ax.set_ylim(-8, offset+8)
    _hide_axis(raster_ax)
    raster_ax.text(-0.085, 0.5, 'Neuron ID', rotation=90,
                   transform=raster_ax.transAxes, va='center', ha='center', fontsize=10)
    # EEG channels: identical scale; remove mean ONLY for visual centering
    window = plot_eeg[:, me]
    demeaned = window - np.mean(window, axis=1, keepdims=True)
    max_abs = np.percentile(np.abs(demeaned), 99.5)
    halfwidth = max(1e-14, 1.25 * max_abs)
    labels = []
    for i in range(4):
        ax = axs[i+5]
        ax.plot((plot_eeg_t[me] - transient_s*1000.)/1000., demeaned[i],
                color=EEG_COLOR if i == 0 else '#65778E',
                linewidth=1.1 if i == 0 else 0.92)
        ax.axhline(0, lw=.55, color='0.85', zorder=0)
        ax.set_ylim(-halfwidth, halfwidth)
        _hide_axis(ax)
        label = f'E{i+1}  #{elec[i]}'
        labels.append(label)
        ax.text(1.008, .5, label, transform=ax.transAxes,
                color=EEG_COLOR if i == 0 else '#65778E',
                va='center', ha='left', fontsize=12, clip_on=False)
    eeg_scale = _nice_scale(halfwidth * .7)
    _vertical_scalebar(axs[-1], eeg_scale, _format_uv(eeg_scale),
                       x_frac=-0.012, fontsize=8)
    # Common time scale bar, bottom
    ax = axs[-1]
    bar_len = 1.0 if stop_s-start_s >= 2. else .2
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    ax.plot([start_s, start_s+bar_len], [-0.15, -0.15],
            color='black', lw=1.6, transform=trans, clip_on=False)
    ax.text(start_s+bar_len/2, -0.25, f'{bar_len:g} s',
            transform=trans, ha='center', va='top', fontsize=9, clip_on=False)
    axs[-1].set_xlim(xlims)
    fig.text(0.04, 0.94, 'A', weight='bold', fontsize=15)
    fig.text(0.04, 0.65, 'B', weight='bold', fontsize=15)
    fig.text(0.04, 0.34, 'C', weight='bold', fontsize=15)
    if save_prefix:
        fig.savefig(f'{save_prefix}.svg', bbox_inches='tight')
        fig.savefig(f'{save_prefix}.png', dpi=300, bbox_inches='tight')
    return fig, {'voltage': dict(zip(VOLT_ORDER, axs[:4])),
                 'raster': raster_ax, 'eeg': axs[5:]}


def _mesh_vertices_faces(nyhead, mesh_name='cortex75K'):
    """Get true NYHead triangulation, stored as MATLAB 1-based indices."""
    block = nyhead.head_data[mesh_name]
    raw_v = np.asarray(block['vc'], dtype=float)
    vertices = raw_v.T if raw_v.shape[0] == 3 else raw_v
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError('NYHead mesh vertices must have shape (N,3)')
    raw_f = np.asarray(block['tri'], dtype=np.int64)
    faces = raw_f.T if raw_f.shape[0] == 3 else raw_f
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError('NYHead mesh triangle indices must have shape (F,3)')
    if faces.min() == 1:
        faces = faces - 1
    if faces.min() < 0 or faces.max() >= len(vertices):
        raise ValueError('Invalid mesh triangle indices')
    return vertices, faces


def _mesh_artist(ax, v, tri, max_faces=45000, alpha=.20, color='#A8B5C5', seed=3):
    if len(tri) > max_faces:
        rng = np.random.default_rng(seed)
        keep = np.sort(rng.choice(len(tri), max_faces, replace=False))
        tri = tri[keep]
    # Surface-normal illumination retains gyral/sulcal detail in a still image.
    pts = v[tri]
    fn = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    light = np.array([-0.45, .25, .86])
    light /= np.linalg.norm(light)
    shade = 0.70 + 0.30 * (0.5 + 0.5 * (fn @ light))
    rgba = np.empty((len(pts), 4))
    rgba[:, :3] = np.asarray(to_rgb(color))[None, :] * shade[:, None]
    rgba[:, 3] = alpha
    collection = Poly3DCollection(pts, facecolors=rgba,
                                  edgecolors='none', linewidths=0,
                                  zsort='average')
    ax.add_collection3d(collection)
    return collection


def plot_nyhead_source_electrodes(nyhead, electrode_ids, distances_mm=None,
                                  target_mni=None, local_radius_mm=55.,
                                  save_prefix=None, figsize=(13, 6.7)):
    """Actual NYHead cortical triangles: whole-brain and source-local views.

    The local plot uses triangles whose centroid is within local_radius_mm.
    Some scalp contacts can lie outside this sphere; axis limits include them.
    """
    figure_style()
    source = np.asarray(nyhead.dipole_pos, dtype=float).reshape(3)
    normal = np.asarray(nyhead.cortex_normal_vec, dtype=float).reshape(3)
    normal = normal / np.linalg.norm(normal)
    elecs = np.asarray(nyhead.elecs[:3, :], dtype=float).T
    ids = np.asarray(electrode_ids, dtype=int)
    selected_pos = elecs[ids]
    d = np.linalg.norm(selected_pos - source, axis=1) if distances_mm is None else np.asarray(distances_mm)
    v, tri = _mesh_vertices_faces(nyhead, 'cortex75K')
    if target_mni is not None:
        error_mm = np.linalg.norm(source-np.asarray(target_mni))
        if error_mm > 2:
            warnings.warn(f'Target point is {error_mm:.2f} mm from selected cortical vertex')

    fig = plt.figure(figsize=figsize)
    axes = [fig.add_subplot(121, projection='3d'), fig.add_subplot(122, projection='3d')]
    colors = ['#B45309', '#274C77', '#6799C3', '#8B5CF6']
    # Whole cortical surface, with actual mesh triangles (subsampled for display)
    _mesh_artist(axes[0], v, tri, max_faces=55000, alpha=.12)
    # Local cortical mesh patch
    triangle_centers = v[tri].mean(axis=1)
    local = np.linalg.norm(triangle_centers-source, axis=1) < local_radius_mm
    if not np.any(local):
        raise RuntimeError('No cortical faces near chosen dipole source')
    _mesh_artist(axes[1], v, tri[local], max_faces=30000, alpha=.31, color='#9DAEC0')

    for k, ax in enumerate(axes):
        ax.scatter(*source, color='#D55E00', marker='*', s=175,
                   depthshade=False, zorder=10, label='Cortical source')
        ax.quiver(*source, *(normal*13), color='#D55E00', linewidth=2.3,
                  arrow_length_ratio=.20)
        for i, pos in enumerate(selected_pos):
            ax.scatter(*pos, color=colors[i % 4], marker='o', s=55,
                       edgecolors='black', linewidths=.5, depthshade=False,
                       label=f'E{i+1} #{ids[i]} ({d[i]:.1f} mm)')
            # Electrode label adjacent to surface contact
            ax.text(*(pos+np.array([1.4, 0, 2.6])), f'E{i+1}',
                    color=colors[i % 4], fontsize=10, weight='bold')
        if k == 0:
            ext = np.vstack([v, selected_pos, source])
            margin = 8.
            ax.set_title('A  NYHead cortical surface + selected EEG contacts', fontsize=12)
            ax.view_init(elev=18, azim=185)
        else:
            ext = np.vstack([v[np.unique(tri[local].ravel())], selected_pos, source])
            margin = 5.
            ax.set_title('B  Source and local cortical surface', fontsize=12)
            ax.view_init(elev=21, azim=220)
        low = ext.min(axis=0) - margin
        high = ext.max(axis=0) + margin
        center = (low+high)/2
        rad = max(high-low)/2
        for setter, c in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), center):
            setter(c-rad, c+rad)
        ax.set_box_aspect((1,1,1), zoom=.88)
        ax.set_xlabel('MNI x (mm)', labelpad=1)
        ax.set_ylabel('MNI y (mm)', labelpad=1)
        ax.set_zlabel('MNI z (mm)', labelpad=1)
        ax.tick_params(labelsize=7)
        ax.grid(False)
        # Transparent panes
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.pane.fill = False
            axis.pane.set_edgecolor('0.85')
    axes[1].legend(loc='upper center', bbox_to_anchor=(.5, -.04),
                   ncol=2, frameon=False, fontsize=8)
    fig.subplots_adjust(left=.02, right=.99, top=.92, bottom=.16, wspace=.02)
    if save_prefix:
        fig.savefig(f'{save_prefix}.png', dpi=280, bbox_inches='tight')
        fig.savefig(f'{save_prefix}.svg', bbox_inches='tight')
    return fig, axes


def plot_four_electrode_psd(eeg_uV, eeg_time_ms, electrode_ids, transient_s=1.,
                            maximum_frequency_hz=200., save_prefix=None):
    """Optional follow-up PSD; uses full, un-downsampled EEG time series.

    PSD units: µV²/Hz. Uses a common sampling setup for all electrodes.
    """
    figure_style()
    ids = np.asarray(electrode_ids, dtype=int)
    time_ms = np.asarray(eeg_time_ms, dtype=float)
    fs = 1000. / np.median(np.diff(time_ms))
    mask = time_ms >= transient_s * 1000
    x = np.asarray(eeg_uV, dtype=float)[:, mask]
    if x.shape[0] != len(ids):
        raise ValueError('PSD requires EEG channel count to equal number of ids')
    if x.shape[1] < 8:
        raise ValueError('Insufficient post-transient samples')
    # Downsample only if useful; anti-aliased by resample_poly
    target_fs = max(4. * maximum_frequency_hz, 1000.)
    if target_fs < fs:
        ratio = Fraction(target_fs / fs).limit_denominator(100000)
        x = resample_poly(x, ratio.numerator, ratio.denominator, axis=-1)
        fs = fs * ratio.numerator / ratio.denominator
    # High-pass 0.5 Hz without removing frequencies within requested band
    sos = butter(3, 0.5, btype='highpass', fs=fs, output='sos')
    x = sosfiltfilt(sos, x, axis=-1)
    nperseg = min(x.shape[1], max(16, round(fs * 2)))
    f, spectra = welch(x, fs=fs, window='hann', nperseg=nperseg,
                       noverlap=nperseg//2, detrend='constant', axis=-1)
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    for i, id_ in enumerate(ids):
        mask_f = (f >= .5) & (f <= maximum_frequency_hz)
        db = 10 * np.log10(np.maximum(spectra[i, mask_f], np.finfo(float).tiny))
        ax.plot(f[mask_f], db, lw=1.3, label=f'E{i+1} #{id_}')
    ax.set(xlabel='Frequency (Hz)', ylabel='PSD (dB re 1 µV²/Hz)',
           title='Simulated scalp EEG — four selected electrodes')
    ax.legend(frameon=False, ncol=2)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    if save_prefix:
        fig.savefig(f'{save_prefix}.svg', bbox_inches='tight')
        fig.savefig(f'{save_prefix}.png', dpi=300, bbox_inches='tight')
    return fig, ax, (f, spectra)
