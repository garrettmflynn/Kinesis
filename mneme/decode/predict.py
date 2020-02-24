'''
Functions to predict information from brain data. 
Adapted from Sentdex BCI repository (https://github.com/Sentdex/BCI)

Author: Garrett Flynn
Date: 15 February 2020
'''


import tensorflow as tf
import numpy as np

def predict(model = None,feature=None,categories = None):
    channels = len(feature)
    times = len(feature[0][0])
    reshape = (-1, channels, times)

    network_input = np.array(feature).reshape(reshape)
    out = model.predict(network_input)

    choice = np.argmax(out)
    prediction = categories[choice]

    return prediction