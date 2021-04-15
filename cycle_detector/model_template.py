# ------------------------------------------ This app is a cycle detector --------------------------------------------
# Simple API. JSON Request with following format:
# {
#     'year': "2020",
#     'month': "12",
#     'day': "24",


import pandas as pd
import numpy as np
from flask import Flask,jsonify,json,request
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import SGD,Adam
import requests,os, datetime
from tensorflow.keras import layers
from tensorflow.keras.models import load_model
import os,random
from scipy.signal import find_peaks
import tensorflow as tf

window_size = 3600
resolution = 20
margin = 20

def CONV1D_model(window_size):
  model_m = Sequential()

  model_m.add(Conv1D(filters=64, kernel_size=8, activation='relu',input_shape=(window_size,1)))
  model_m.add(keras.layers.Dropout(0.3))
  model_m.add(BatchNormalization())
  model_m.add(Conv1D(filters=32,kernel_size=4,activation='relu'))
  model_m.add(keras.layers.Dropout(0.3))
  model_m.add(MaxPooling1D(pool_size=4))
  model_m.add(BatchNormalization())
  model_m.add(Conv1D(filters=16,kernel_size=2,activation='relu'))
  model_m.add(keras.layers.Dropout(0.3))
  model_m.add(Flatten())
  model_m.add(keras.layers.Dense(8, activation='relu'))
  model_m.add(keras.layers.Dense(1, activation='sigmoid'))
  model_m.summary()

  return model_m  

def DeepAnt_Model():
  model_m = keras.Sequential(
      [
          layers.Input(shape=(X.shape[1], X.shape[2])),
          #layers.BatchNormalization(),
          layers.Conv1D(
              filters=32, kernel_size=7, padding="same", strides=1, activation="relu"
          ),
          #layers.Dropout(rate=0.2),
          layers.MaxPool1D(pool_size=2),
          layers.Conv1D(
              filters=32, kernel_size=7, padding="same", strides=1, activation="relu"
          ),
          layers.MaxPool1D(pool_size=2),
          layers.Flatten(),
          layers.Dropout(rate=0.25),
          layers.Dense(128, activation='relu'),
          layers.Dropout(rate=0.45),
          layers.Dense(window_size-2*margin, activation='relu'),
      ]
  )
  model_m.compile(optimizer=keras.optimizers.Adam(learning_rate=0.0005), loss="mse")
  model_m.summary()
  return model_m
