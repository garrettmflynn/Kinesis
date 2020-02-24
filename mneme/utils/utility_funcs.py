# -*- coding:utf-8 -*-
'''
This module defines multiple utility function for dealing with Traces
'''

import neo
import numpy as np
import quantities as pq

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]

def unzip_neo(neo):

    data = neo.read(lazy=False)[0]

    for seg in data.segments:
        for asig in seg.analogsignals:
            raw_sigs = asig
    # channel_indexes = None  # could be channel_indexes = [0]
    # raw_sigs = neo.get_analogsignal_chunk(block_index=0, seg_index=0, i_start=1024, i_stop=2048,
    #                                         channel_indexes=channel_indexes)
    # float_sigs = neo.rescale_signal_raw_to_float(raw_sigs, dtype='float64')
    # sampling_rate = neo.get_signal_sampling_rate()
    # t_start = neo.get_signal_t_start(block_index=0, seg_index=0)
    # units = neo.header['signal_channels'][0]['units']
    
    return raw_sigs

def RAM(reader):
# AFTER LOADING AN .NEX FILE VIA 
# events = neo.io.get_io(epoch_bounds)
   
    ## Pull out events
    reader.parse_header()
    nb_event_channel = reader.event_channels_count()

    events = {}

    for chan_index in range(nb_event_channel):
        nb_channel = reader.header['event_channels'][chan_index][0];
        event_name = None
        if 'nr' not in nb_channel:
            a = ['DIO_00002','DIO_65533']
            if any(x in nb_channel for x in a):
                event_name = 'ITI_ON'
            if any(x in nb_channel for x in ['DIO_00004','DIO_65531']):
                event_name = 'FOCUS_ON'
            if any(x in nb_channel for x in ['DIO_00008','DIO_65527']):
                event_name = 'SAMPLE_ON'
            if any(x in nb_channel for x in ['DIO_00016','DIO_65519']):
                event_name = 'SAMPLE_RESPONSE'
            if any(x in nb_channel for x in ['DIO_00032','DIO_65503']):
                event_name = 'MATCH_ON'
            if any(x in nb_channel for x in ['DIO_00064','DIO_65471']):
                event_name = 'MATCH_RESPONSE'
            if any(x in nb_channel for x in ['DIO_00128','DIO_65407']):
                event_name = 'CORRECT_RESPONSE'
            if any(x in nb_channel for x in ['DIO_00256','DIO_65279']):
                event_name = 'END_SESSION'
            if any(x in nb_channel for x in ['DIO_Changed','DIO_65533']):
                event_name = 'DIO_CHANGED'

            times = reader.get_event_timestamps(block_index=0, seg_index=0,
                                                event_channel_index=chan_index,
                                                t_start=None,
                                                t_stop=None)
            times = reader.rescale_event_timestamp(times[0], dtype='float64')
            events[event_name] = times

    trial_markers = ['FOCUS_ON','MATCH_RESPONSE']
    marker_of_interest = 'SAMPLE_RESPONSE'
    num_trials = len(events[trial_markers[0]])
    trials = np.empty([2,num_trials])
    roi = np.empty([2, num_trials])
    for trial in range(num_trials):
            trials[0,trial] = events[trial_markers[0]][trial]
            trials[1, trial] = events[trial_markers[1]][trial]
            roi[0, trial] = events[marker_of_interest][trial]-1
            roi[1, trial] = events[marker_of_interest][trial]+1

    print('Done parsing RAM events')
    ## Break reader into CA1 and CA3 segments

    bl = reader.read(lazy=False)[0]
    for seg in bl.segments:
        print(seg)


    return trials, roi