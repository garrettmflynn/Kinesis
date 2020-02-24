import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp2d

def analog_signal(x=None,y=None):
    plt.figure()
    print('Only for channel #1')
    plt.plot(x, y)
    plt.title('Signal Test')
    plt.ylabel('Voltage')
    plt.xlabel('Time (s)')

    plt.show()
    return

def spectrum(x=None,y=None,z=None,voltage_units= 'mV',resIncrease=8,clims=(-5,5)):

    print('Only for channel #1')

    # plt.subplot(2, 1, 1)
    z = np.transpose(z[0,:,:])
    # plt.pcolormesh(x, y, z,cmap='RdBu_r')
    # bar = plt.colorbar()
    # bar.set_label('Z-Score of Power')
    # plt.clim(clims)
    # plt.title('Test Spectrograms')
    # plt.ylabel('Frequency (Hz)')
    # plt.xlabel('Time (s)')
    # #plt.ylim((details['min_STFT'], details['max_STFT']))

    x2 = np.linspace(x[0], x[-1], int(len(x) * resIncrease))
    y2 = np.linspace(y[0], y[-1], int(len(y) * resIncrease))
    f = interp2d(x, y, z, kind='linear')
    Z2 = f(x2, y2)
    # plt.subplot(2, 1, 2)
    X2, Y2 = np.meshgrid(x2, y2)
    plt.pcolormesh(X2, Y2, Z2,cmap='RdBu_r')
    plt.clim(clims)
    bar = plt.colorbar()
    bar.set_label('Z-Score of Power')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    #plt.ylim((details['min_STFT'], details['max_STFT']))

    plt.show()

    return