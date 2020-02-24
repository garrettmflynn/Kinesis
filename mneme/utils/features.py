import numpy as np
from scipy import signal
import quantities as pq

def lfp(data=None,details=None):
    lfp = np.empty(data.shape)
    for row in range(np.size(data, 0)):
        lfp[row, :] = butter_bandpass_filter(data[row, :],
                                            details['min_Bandpass'],
                                            details['max_Bandpass'],
                                            details['rate'],
                                            order=5)

def stft(data=None,t=None,rate = None, t_bin=None,lims=(0,150)):

    N = 1e5
    amp = 2 * np.sqrt(2)
    noise_power = 0.01 * rate / 2
    time = np.arange(N) / float(rate)
    mod = 500 * np.cos(2 * np.pi * 0.25 * time)
    carrier = amp * np.sin(2 * np.pi * 3e3 * time + mod)
    noise = np.random.normal(scale=np.sqrt(noise_power),
                                size=time.shape)
    noise *= np.exp(-time / 5)
    x = carrier + noise

    window= int(t_bin * rate)
    c_len = data.shape[0]

    for row in range(len(data)):
        temp_f, temp_t, temp_Zxx = signal.spectrogram(data[row, :],
                                                        rate,
                                                        'hann', nperseg=window)

        freq_slice = np.where((temp_f >= lims[0]) & (temp_f <= lims[1]))
        Zxx = temp_Zxx[freq_slice, :][0]
        del temp_Zxx

        if row == 0:
            power = np.empty([c_len, np.shape(Zxx)[1], np.shape(Zxx)[0]], dtype=float)
            f = temp_f[freq_slice] * pq.Hz
            t = temp_t * pq.s
        del temp_t
        del temp_f
        power[row, :, :] = np.transpose(Zxx ** 2)
        del Zxx

    return power, f,t,window


def normalize(data=None,method='ZSCORE',log = False):
    if log:
        data = 10*np.log10(data)
    if method == 'ZSCORE':
        freqMu = np.mean(data,axis=1)
        freqSig = np.std(data,axis=1)

        for channel in range(len(data)):
            data[channel,:,:] = (data[channel] - freqMu[channel])/freqSig[channel]

    return data