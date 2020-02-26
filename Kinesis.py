import sys
import mneme
import os
from mneme.core import Trace
from mneme.utils import realtime_streams, features, plots
import quantities as pq
import numpy as np
import pickle


TAG = 'MOVEMENT'
                        # Streams
                            # OPENBCI
                            # SYNTHETIC
STREAM = 'SYNTHETIC' 
                        # Ports
                            # Mac: '/dev/cu.usbserial-DM01N7AE'
                            # Windows: 'COM4'
                            # Synthetic: None
PORT = None

PLOTS = False

# Initialize the Trace
trace = Trace(id = 'User',tag=TAG)

# Capture New Trace on OpenBCI
print('Gathering Training and Validation Data...')

if STREAM == 'SYNTHETIC':
    trace.capture(stream=STREAM)
elif STREAM == 'OPENBCI':
    trace.capture(stream=STREAM,port=PORT)

print('Training Data Gathered!')


## Extract Features
trace.details['min_STFT'] = 0
trace.details['max_STFT'] = 40
trace.details['timebin'] = .1 # 100 ms 
trace.details['overlap'] = trace.details['timebin']/2
trace.details['rate'] = len(trace.data[0])/(trace.details['time_channel'][-1]) # Derived rate (do not trust Brainflow)

print('Sampling Rate: ')
print(trace.details['rate'])

feats, trace.details['f'],trace.details['t'],trace.details['window'] = features.stft(data=trace.data,t=trace.details['time_channel'],rate = trace.details['rate'],t_bin=trace.details['timebin'],lims=(trace.details['min_STFT'],trace.details['max_STFT']))
feats = features.normalize(data=feats,method='ZSCORE',log=True)
data_labels = realtime_streams.map_events_to_features(event_times=trace.details['event_times'],data_times=trace.details['t'],events=trace.details['Events'][0])

# Plot signals and features if desired
if PLOTS:
    plots.analog_signal(x = trace.details['time_channel'],y = trace.data[1])
    plots.spectrum(trace.details['t'],trace.details['f'], feats,resIncrease=4,voltage_units=trace.details['voltage_units'],clims=(-5,5))

## Train the Model
results = {}
model,training_params = mneme.decode.train.train_cnn(feats,data_labels)

## Use Model for Next OpenBCI Run

trace = Trace(id = 'User',tag=TAG)
trace.details['min_STFT'] = 0
trace.details['max_STFT'] = 40
trace.details['timebin'] = .1 # 100 ms
trace.details['overlap'] = trace.details['timebin']/2

if STREAM == 'SYNTHETIC':
    trace.capture(stream='SYNTHETIC',model=model,categories=training_params['categories'],details=trace.details)
elif STREAM == 'OPENBCI':
    trace.capture(stream='OPENBCI',port=PORT,model=model,categories=training_params['categories'],details=trace.details)

print(trace.details['performance'])