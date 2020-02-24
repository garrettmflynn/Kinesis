'''
Functions to train a machine learning model to decode information from brain data. 
Adapted from Sentdex BCI repository (https://github.com/Sentdex/BCI)

Author: Garrett Flynn
Date: 15 February 2020
'''


import numpy as np
import neo
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv1D, MaxPooling1D, BatchNormalization
import os
import random
import time

def train_cnn(features=None,labels=None):
    print('Training CNN')
    channels = len(features)
    frequencies = len(features[0][0])
    reshape = (-1, channels, frequencies)

    print("split features into training and testing datasets")
    
    # Defining training and test data
    indices = np.arange(len(labels))
    if len(indices)%2 != 0:
        indices = indices[0:-1]
    np.random.shuffle(indices)
    train_inds,test_inds = np.split(indices,2)
    traindata,categories = get_data(features=features[:,train_inds,:],LABELS=labels[test_inds])
    
    # Getting training and test data
    train_X = []
    train_y = []
    testdata, categories = get_data(features=features[:,test_inds,:],LABELS=labels[test_inds])
    test_X = []
    test_y = []
    for X, y in traindata:
        train_X.append(X)
        train_y.append(y)
    for X, y in testdata:
        test_X.append(X)
        test_y.append(y)

    print(len(train_X))
    print(len(test_X))


    print(np.array(train_X).shape)
    train_X = np.array(train_X).reshape(reshape)
    test_X = np.array(test_X).reshape(reshape)

    train_y = np.array(train_y)
    test_y = np.array(test_y)

    model = Sequential()

    model.add(Conv1D(64, (3), input_shape=train_X.shape[1:]))
    model.add(Activation('relu'))

    model.add(Conv1D(64, (2)))
    model.add(Activation('relu'))
    model.add(MaxPooling1D(pool_size=(2)))

    model.add(Conv1D(64, (2)))
    model.add(Activation('relu'))
    model.add(MaxPooling1D(pool_size=(2), padding='same'))

    model.add(Flatten())

    model.add(Dense(512))

    model.add(Dense(3))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy'])

    epochs = 10
    batch_size = 32
    for epoch in range(epochs):
        model.fit(train_X, train_y, batch_size=batch_size, epochs=1, validation_data=(test_X, test_y))
        score = model.evaluate(test_X, test_y, batch_size=batch_size)
    MODEL_NAME = f"models/{round(score[1]*100,2)}-{epoch}epoch-{int(time.time())}-loss-{round(score[0],2)}.model"
    model.save(MODEL_NAME)
    print("saved:")
    print(MODEL_NAME)

    training_params = {}
    training_params['categories'] = categories
    training_params['train_inds'] = train_inds
    training_params['train_inds'] = test_inds

    return model, training_params

def get_data(features=None,LABELS=None):
    training_data = {}
    CATEGORIES = []

    for ii in range(len(LABELS)):
        if LABELS[ii] != '':
            if LABELS[ii] not in training_data:
                training_data[LABELS[ii]] = []
                CATEGORIES.append(LABELS[ii])

            training_data[LABELS[ii]].append(features[:,ii,:])

    # Begin focusing on specific categories 

    lengths = [len(training_data[category]) for category in CATEGORIES]
    print(lengths)

    print('Not proper derivation of validation dataset')
    for category in CATEGORIES:
        np.random.shuffle(training_data[category])
        training_data[category] = training_data[category][:min(lengths)]

    lengths = [len(training_data[category]) for category in CATEGORIES]
    print(lengths)

    # creating X, y 
    combined_data = []
    for ii in range(len(CATEGORIES)):
        for data in training_data[CATEGORIES[ii]]:
            binary_categories = np.zeros(len(CATEGORIES))
            binary_categories[ii] = 1
            combined_data.append([data, binary_categories])


    np.random.shuffle(combined_data)
    print("length:",len(combined_data))

    return combined_data, CATEGORIES

