import numpy as np 
import scipy
import sys
import os

def get_size(file):
    """
    Retorna o tamanho em megabytes de um dicionário e seus valores.

    Args:
        file (string): caminho do arquivo.

    Returns:
        float: O tamanho do dicionário e seus valores em megabytes.

    Raises:
        None
    """
    try:
        file_stats = os.stat(file)
        file_size = file_stats.st_size
        print(f"File Size is {file_size / (1024 * 1024):.2f}MB")
    except FileNotFoundError:
        print("File not found.")

def get_numpy(data):
    """
    Converte os dados em formato de dicionário para matrizes NumPy.

    Args:
        data (dict): Dados no formato JSON armazenados em um tipo dicionário contendo informações sobre os valores de tensão de simulação.

    Returns:
        tuple: Uma tupla contendo um array NumPy representando os tempos e uma matriz NumPy representando os valores de tensão.
    """
    mapa = np.zeros((len(data['simData']['V_soma']), len(data['simData']['t'])))
    t = np.array(data['simData']['t'])
    for i, value in enumerate(data['simData']['V_soma'].values()):
        mapa[i] = value
    return t, mapa

def find_peaks(t_arr, v_arr, only_id=False):
    """
    Encontra os picos em um sinal de forma de onda.

    Args:
        t_arr (array-like): Uma matriz de tempos correspondentes aos valores do sinal de forma de onda.
        v_arr (array-like): Uma matriz de valores do sinal de forma de onda.
        only_id (bool, optional): Indica se apenas os IDs dos picos devem ser retornados. O padrão é False.

    Returns:
        tuple or numpy.ndarray: Se only_id for False, retorna uma tupla contendo os IDs dos picos, tempos correspondentes e valores correspondentes. Se only_id for True, retorna apenas os IDs dos picos.
    """
    peaks_id, _ = scipy.signal.find_peaks(v_arr, height=0)
    t = t_arr[peaks_id]
    v = v_arr[peaks_id]
    if only_id:
        peaks_id
    else:
        return peaks_id, t, v


def phase_of_v(t_sample, v_sample, return_peaks=False):
    """
    Calcula as fases de um sinal de forma de onda em relação aos picos.

    Args:
        t_sample (array-like): Uma matriz de tempos correspondentes aos valores do sinal de forma de onda.
        v_sample (array-like): Uma matriz de valores do sinal de forma de onda.

    Returns:
        numpy.ndarray: Uma matriz contendo as fases calculadas para cada neurônio em relação aos picos.

    Raises:
        None
    """
    peaksmat, t_peaks = [], [],  # listas para encontrar id e tempo dos picos
    for v in v_sample:
        peaks_id, t_peak, _ = find_peaks(t_sample, v)
        peaksmat.append(peaks_id)
        t_peaks.append(t_peak)
    id_first_spk = max([min(peak) for peak in peaksmat]) # dos menore spk o maior
    id_last_spk = min([max(peak) for peak in peaksmat]) # id do primeiro dos ultimos spk 

    t_range = t_sample[id_first_spk:id_last_spk]  # tempo onde a phase é definida
    phi = lambda t, t0, t1 : 2*np.pi*(t-t0)/(t1 - t0)  # calcular fase
    phases = np.zeros((len(peaksmat), len(t_range)))  # phases dos n neurônios

    # para cada id do pico n-esimo neuronio
    for n, peak in enumerate(peaksmat):
        # para cada ISI do neurônio
        for t0, t1 in zip(t_sample[peak][:], t_sample[peak][1:]):
            # para cada tempo i onde definimos a fase:
            for i, t in enumerate(t_range):
                if t0 < t <t1:
                    # calcula a fase phi e adiciona no array
                    phases[n,i] = phi(t,t0,t1)
    if return_peaks:
        return t_range, phases, peaksmat, t_peaks, id_first_spk, id_last_spk
    else:    
        return t_range, phases


def kuramoto_param_global_order(spatial_phase_arr):
    """
    Calculates the global order parameter of Kuramoto for a set of spatial phases.

    Args:
        spatial_phase_arr (numpy.ndarray): Array representing the spatial phase distribution of neurons.

    Returns:
        float: Value of the global order parameter of Kuramoto.

    """
    n = len(spatial_phase_arr)
    somatorio = 0
    for j in range(n):
        j = j % n
        somatorio += np.exp(complex(0, spatial_phase_arr[j]))
    z = np.abs(somatorio) / n
    return z

def kuramoto_param_local_order(spatial_phase_arr, delta):
    """
    Calculates the Kuramoto parameter order for a given spatial phase distribution.

    Args:
        spatial_phase_arr (numpy.ndarray): Array representing the spatial phase distribution of neurons.
        delta (int): Window of neighboring neurons to consider.

    Returns:
        numpy.ndarray: Array of Kuramoto parameter order values for each neuron.
    """
    n = len(spatial_phase_arr)
    z = np.zeros_like(spatial_phase_arr)

    for i in range(n):
        somatorio = 0
        for vizinhos in range(i - delta, i + delta + 1):
            j = vizinhos % n
            somatorio += np.exp(complex(0, spatial_phase_arr[j]))
        z[i] = np.abs(somatorio / (int(2*delta)+1))
    return z


def mean_lop_window(lop, window):
    """
    Calcula a média de janelas deslizantes em um conjunto de dados.

    Args:
        lop (numpy.ndarray): Array contendo os dados do parâmetro de ordem local (LOP)
        window (int): O tamanho da janela deslizante.
        ti (float): O valor inicial da janela de tempo.
        tf (float): O valor final da janela de tempo.

    Returns:
        tuple: Uma tupla contendo um array NumPy representando os tempos das janelas e um array NumPy representando a média dos dados em cada janela.

    Raises:
        None
    """
    n_arrays = lop.shape[0] // window
    lop_window = np.array_split(lop, n_arrays)
    mlw = np.zeros((n_arrays,lop.shape[1]))
    for i, arr_window in enumerate(lop_window):
        mlw[i] = np.mean(arr_window, axis=0)
    mlw = np.transpose(mlw)
    return mlw