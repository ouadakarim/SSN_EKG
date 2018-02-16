# -*- coding: utf-8 -*-
from ecgprocessing import processing_utils


class ECGSignal(object):
    """ The ECGSignal class represents an ECG signal and is
    responsible for calculating the parameters of the signal
    i.e:
        - Heart rate
        - R-peaks
    """
    def __init__(self, ecg_signal_sample_nr):
        """ You should use the filtered signal"""
        self.data = processing_utils.get_signal(ecg_signal_sample_nr)
        self.signal_parameters = self.process_signal()
        # Heart rate
        self.heart_rate = self.signal_parameters['heart_rate']
        self.heart_rate_ts = self.signal_parameters['heart_rate_ts']
        self.heart_rate_avg = sum(self.heart_rate) / float(len(self.heart_rate))
        # R-peaks
        self.rpeaks = self.signal_parameters['rpeaks']

    def process_signal(self):
        """ Processes the input signal and extracts it's parameters"""
        return processing_utils.get_data_biosppy(self.data)


