import sys
import mneme
import os
from mneme.core import Trace
from mneme.utils import realtime_streams, features, plots
import quantities as pq
import numpy as np
import pickle


# Gather Training and Validation Data
print('Gathering Training and Validation Data...')
TAG = 'MOVEMENT'

# Initialize the Memory
memory = Trace(id = 'Garrett')

# Capture New Memory on OpenBCI
memory.capture(stream='SYNTHETIC')
#memory.capture(stream='OPENBCI',port='/dev/tty.usbserial-DM01N7AE')

print('Training and Validation Data Gathered!')


## Extract Features
#memory = np.load('/Users/garrettflynn/Desktop/MOUSAI/Mneme/moments/OpenBCI_Testcaptured',allow_pickle=True)

memory.details['min_Bandpass'] = 1 # Doesn't do anything right now
memory.details['max_Bandpass'] = 250 # Doesn't do anything right now
memory.details['min_STFT'] = 0
memory.details['max_STFT'] = 40
memory.details['timebin'] = .1 # 100 ms = .1 for blackrock
memory.details['freqbin'] = .5 # Doesn't do anything right now
memory.details['overlap'] = memory.details['timebin']/2
memory.details['rate'] = len(memory.data[0])/(memory.details['time_channel'][-1]) # Derived rate (do not trust Brainflow)
print('Sampling Rate: ')
print(memory.details['rate'])

#memory.data = mneme.utils.filters.butter_bandpass_filter(memory.data, 59.0, 61.0, memory.details['rate'], order=5)
#plots.analog_signal(x = memory.details['time_channel'],y = memory.data[3])
feats, memory.details['f'],memory.details['t'],memory.details['window'] = features.stft(data=memory.data,t=memory.details['time_channel'],rate = memory.details['rate'],t_bin=memory.details['timebin'],lims=(memory.details['min_STFT'],memory.details['max_STFT']))
feats = features.normalize(data=feats,method='ZSCORE',log=True)
#plots.spectrum(memory.details['t'],memory.details['f'], feats,resIncrease=4,voltage_units=memory.details['voltage_units'],clims=(-5,5))
data_labels = realtime_streams.map_events_to_features(event_times=memory.details['event_times'],data_times=memory.details['t'],events=memory.details['Events'][0])

prev_details = memory.details

## Train the Model
results = {}
model,training_params = mneme.decode.train.train_cnn(feats,data_labels)

## Use Model for Next OpenBCI Run

#MODEL_NAME = "/Users/garrettflynn/Desktop/MOUSAI/Mneme/models/33.33-9epoch-1582244188-loss-1.28.model"
#model = tf.keras.models.load_model(MODEL_NAME)
## Load Model Parameters
#model_params = np.load('/Users/garrettflynn/Desktop/MOUSAI/Mneme/models/OpenBCI_02_20_20.pkl')

TAG = 'MOVEMENT'

memory = Trace(id = 'Garrett',tag='MOVEMENT')

memory.details['min_Bandpass'] = 1
memory.details['max_Bandpass'] = 250
memory.details['min_STFT'] = 0
memory.details['max_STFT'] = 40
memory.details['timebin'] = .1 # 100 ms = .1 for blackrock
memory.details['freqbin'] = .5
memory.details['overlap'] = memory.details['timebin']/2

memory.capture(stream='SYNTHETIC',model=model,categories=training_params['categories'],details=memory.details)
#memory.capture(stream='OPENBCI',port='/dev/tty.usbserial-DM01N7AE',model=model,categories=training_params['categories'],details=memory.details)

print(memory.details['performance'])