import numpy as np
import matplotlib.pyplot as plt
from biosppy.signals import ecg


def get_data_biosppy(signal, sampling_rate=500., show_plot=False):
    """ Get ECG signal parameters using the biosppy library"""
    return ecg.ecg(signal=signal, sampling_rate=sampling_rate, show=show_plot)


def show_sample_plot(signal):
    """ Example - retrieve ECG data and show it as a standard plot"""
    plt.plot(signal)
    plt.show()


def get_signal(sample_nr):
    """ Retrieve ECG data
    NOTE: Because there are 310 samples the sample_nr
    should be between 0 and 309 """
    if 0 <= sample_nr < 310:
        ecg_data = np.load('data/filtered.npy')
        return ecg_data[sample_nr]
    else:
        return None








