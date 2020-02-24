""" 
This module defines :class:'Trace'
"""

import sys
import imutils
import numpy as np
import time
import cv2
import os
import neo
from mneme.utils.utility_funcs import nan_helper
from mneme.utils.realtime_streams import initialize_board,start_stream,pull_data,stop_stream
from mneme.utils.realtime_viewer import EventManager,query_key
import quantities as pq
from math import cos,sin
import pickle
import datetime

class Trace(object):
    def __init__(self, id='Default',tag=None):
        """
        This is the constructor for the Trace data object,
        which is the pivot around which Mneme functions
        """

        self.id = id
        self.date = datetime.datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
        self.reader = []
        self.data = []
        self.details = {}

    def __repr__(self):
        return "Trace('{},'{}',{})".format(self.id, self.date)

    def __str__(self):
        return '{} _ {}'.format(self.id, self.date)

    def prime(self, attribute, value):
        self.details[attribute] = value

    def capture(self, stream,port=None,model=None,categories=None,details=None):
        print('Initializing board')
        board = initialize_board(stream,port)
        print('Starting stream')
        start_time = start_stream(board)

        command = ' '
        manager = EventManager(advance_command=command,stream_start=start_time,board=board)
        manager.movement()

        print("Quit the event loop by pressing 'q'")
        
        while True:
            manager.update(model=model,categories=categories,details=details)
            # manager.voltage(pull_data(board))
            key = query_key()
            print(key)
            manager.advance(key)

            # Break out of the loop by pressing "q"
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        

        self.details['Events'] = manager.events
        self.details['event_times'] = manager.times
        self.details['performance'] = manager.performance
        manager.destroy()
       
        data = pull_data(board)

        nans, x= nan_helper(data)
        data[nans]= np.interp(x(nans), x(~nans), data[~nans])

        self.data = data[board.eeg_channels] * pq.uV
        self.details['time_channel'] = (data[board.time_channel] - data[board.time_channel][0])*pq.s
        self.details['voltage_units'] = 'uV'
        stop_stream(board,start_time)

        self.save(self.date,'traces')

    def save(self,label=None,datadir='traces'):
        datadir = "traces"
        if not os.path.exists(datadir):
            os.mkdir(datadir)

        print(f"Saving trace...")
        filename = os.path.join(datadir, f"{self.id}{label}")
        with open(filename, "wb") as fp:
            pickle.dump(self, fp)
        print(self.id + " saved!")

    
    def load(self):
        print('Loading ' + self.id + '...')
        self.reader = neo.get_io(filename=self.id)