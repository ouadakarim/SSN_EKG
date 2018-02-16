from ecgprocessing import processing_utils
from ecgprocessing.ECGSignal import ECGSignal

ecg = ECGSignal(40)
print(ecg.rpeaks)
print(ecg.heart_rate_avg)
processing_utils.get_data_biosppy(ecg.data, 500.0, True)


