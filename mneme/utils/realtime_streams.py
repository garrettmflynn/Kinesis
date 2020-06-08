import argparse
import numpy as np
import time
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds

def initialize_board(name='SYNTHETIC',port = None):
    if name == 'OPENBCI':
        board_id = BoardIds.CYTON_DAISY_BOARD.value
        params = BrainFlowInputParams()
        params.serial_port = port
        board_id = BoardIds.CYTON_DAISY_BOARD.value
        board = BoardShim(board_id, params)
        board.rate = BoardShim.get_sampling_rate(board_id)
        board.channels = BoardShim.get_eeg_channels(board_id)
        board.time_channel = BoardShim.get_timestamp_channel(board_id)
        board.eeg_channels = BoardShim.get_eeg_channels(board_id)
        board.accel_channels = BoardShim.get_accel_channels(board_id)

    elif name == 'SYNTHETIC':
        BoardShim.enable_dev_board_logger()

        # use synthetic board for demo
        params = BrainFlowInputParams()
        board_id = BoardIds.SYNTHETIC_BOARD.value
        board = BoardShim(board_id, params)
        board.rate = BoardShim.get_sampling_rate(board_id)
        board.channels = BoardShim.get_eeg_channels(board_id)
        board.time_channel = BoardShim.get_timestamp_channel(board_id)
        board.eeg_channels = BoardShim.get_eeg_channels(board_id)
        board.accel_channels = BoardShim.get_accel_channels(board_id)

    print('Must have OpenBCI GUI open to work... (as port is not opened by Brainflow)')
    board.prepare_session()
    return board

def start_stream(board=None):
    board.start_stream(num_samples=450000)
    start_time = time.time()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    return start_time

def pull_data(board=None,num_samples=450000):
    return board.get_current_board_data(num_samples=num_samples)

def stop_stream(board=None,start_stream=None):
    board.stop_stream()
    stream_time = time.time() - start_stream
    board.release_session()

    return stream_time

def map_events_to_features(event_times=None,data_times = None,events=None):
    curr_timestamp = 1
    prev_timestamp = 0
    closest_data = np.zeros((event_times.size),dtype=int)
    for ii in range(event_times.size):
        while True:
            curr_diff = abs(event_times[ii] - data_times[curr_timestamp])
            prev_diff = abs(event_times[ii] - data_times[prev_timestamp-1])
            if curr_diff < prev_diff:
                curr_timestamp += 1
                prev_timestamp += 1
            if curr_diff > prev_diff:
                closest_data[ii] = int(curr_timestamp)
                curr_timestamp += 1
                prev_timestamp += 1
                break
    
    new_events = np.empty((data_times.size),dtype=str)      
    for ii in range(len(closest_data)-1):
        this_event = closest_data[ii]
        next_event = closest_data[ii+1]
        stop = int(np.floor(this_event + (next_event-this_event)/2))
        if ii == 0:
            start = int(np.floor(this_event))
        else:
            prev_event = closest_data[ii-1]
            start = int(np.floor(this_event + (prev_event-this_event)/2))
        for jj in range(stop-start):
            new_events[start+jj] = events[ii]

    return new_events