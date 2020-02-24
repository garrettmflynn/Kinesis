

'''
Functions to analyze Tensorflow model performance. 
Adapted from Sentdex BCI repository (https://github.com/Sentdex/BCI)

Author: Garrett Flynn
Date: 15 February 2020
'''

import tensorflow as tf
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt


def analyze(model=None,categories=None):

    CLIP = True  # if your model was trained with np.clip to clip  values
    CLIP_VAL = 10  # if above, what was the value +/-

    print('No validation data folder...')
    #VALDIR = 'validation_data'
    PRED_BATCH = 32

    argmax_dict = []
    raw_pred_dict = []
    argmax_pct_dict = []
    for ii in range(len(categories)):
        argmax, raw_pred, argmax_pct = get_val_data(VALDIR, categories[ii], PRED_BATCH)
        argmax_dict.append(argmax)
        raw_pred_dict.append(raw_pred)
        argmax_pct_dict.append(argmax_pct)
    make_conf_mat(argmax_pct_dict,categories)


def get_val_data(valdir, action, batch_size):
    print('get val data is unfinished...')
    argmax_dict = {0: 0, 1: 0, 2: 0}
    raw_pred_dict = {0: 0, 1: 0, 2: 0}

    action_dir = os.path.join(valdir, action)
    for session_file in os.listdir(action_dir):
        filepath = os.path.join(action_dir,session_file)
        if CLIP:
            data = np.clip(np.load(filepath), -CLIP_VAL, CLIP_VAL) / CLIP_VAL
        else:
            data = np.load(filepath) 

        preds = model.predict([data.reshape(-1, 16, 60)], batch_size=batch_size)

        for pred in preds:
            argmax = np.argmax(pred)
            argmax_dict[argmax] += 1
            for idx,value in enumerate(pred):
                raw_pred_dict[idx] += value

    argmax_pct_dict = {}

    for i in argmax_dict:
        total = 0
        correct = argmax_dict[i]
        for ii in argmax_dict:
            total += argmax_dict[ii]

        argmax_pct_dict[i] = round(correct/total, 3)

    return argmax_dict, raw_pred_dict, argmax_pct_dict


def make_conf_mat(argmax_pct_dict,categories):

    action_dict = {}
    for ii in range(len(categories)):
        action_dict[category[ii]] = argmax_pct_dict[ii]
        action_conf_mat = pd.DataFrame(action_dict)
        actions = [i for i in action_dict]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.matshow(action_conf_mat, cmap=plt.cm.RdYlGn)
    ax.set_xticklabels([""]+actions)
    ax.set_yticklabels([""]+actions)

    print("__________")
    print(action_dict)
    for idx, i in enumerate(action_dict):
        print('tf',i)
        for idx2, ii in enumerate(action_dict[i]):
            print(i, ii)
            print(action_dict[i][ii])
            ax.text(idx, idx2, f"{round(float(action_dict[i][ii]),2)}", va='center', ha='center')
    plt.title("Action Thought")
    plt.ylabel("Predicted Action")
    plt.show()
