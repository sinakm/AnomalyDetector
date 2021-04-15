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
from model_template import *

window_size = 3600
resolution = 20
margin = 20

def load_DF (sensorVsCycle,year,month,day):
  url = "172.19.0.1:7770/"+sensorVsCycle+"/fetch_data"
  RawDataRequest = {
    'year': year,
    'month': month,
    'day': day
  }
  response = requests.get(url,json=RawDataRequest).json()
  df1 = pd.DataFrame(data = np.array(response['data']),columns = response['columns'])
  return df1  


@app.route('/cycle_train',methods=['GET'])
def cycle_train():
  days, cycles = [],[]
  random.seed(1)

  url = "172.19.0.1:7770/Cycle/fetch_data"
  days,cycles,X,Y = [],[], [],[] 
  window_size = 3600

  Nays_stamps = np.random.randint(0,86400,90)

  # ----------------------------------------- Cycle Times with Values of 1
  for i in range (1,12,1):
    df1 = load_DF ("Cycle",year,month,str(i))

    A_Positive = df1[df1['Sts']==8].index
    for i in A_Positive:
      if i<(86400-3600):
        cyc = np.array(df1.iloc[i:i+3600]['Cycle']).reshape(-1,1)
      X.append(cyc)
      Y.append(np.array([1]).reshape(-1))
    days.append('2021-1-'+str(i))



  # ---------------------------------------- Other timestamps
  for i in range(0,len(Nays_stamps),1):
    if Nays_stamps[i]<(86400-3600):
      cyc = np.array(df1.iloc[Nays_stamps[i]:Nays_stamps[i]+3600]['Cycle']).reshape(-1,1)
    X.append(cyc)
    Y.append(np.array([0]).reshape(-1))

  X=np.array(X)
  Y=np.array(Y)



  X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state = 1 , shuffle = True)
  model_m = CONV1D_model(window_size)


  temp_H5_Dir = 'model/temp/'
  for file in os.scandir(temp_H5_Dir):
      if file.name.endswith(".h5"):
          os.remove(file)

  opt = Adam(learning_rate=0.01)
  model_m.compile(loss='binary_crossentropy',
                  optimizer=opt, metrics=['accuracy'])

  BATCH_SIZE = 20
  EPOCHS = 100
  callbacks_list = [
      keras.callbacks.ModelCheckpoint(
          filepath='model/temp/best_model.{epoch:02d}-{loss:.2f}.h5',
          monitor='val_loss', save_best_only=True),
      keras.callbacks.EarlyStopping(monitor='val_loss', patience=30)]

  history = model_m.fit(X,
                        Y,
                        batch_size=BATCH_SIZE,
                        callbacks=callbacks_list,
                        epochs=EPOCHS,
                        validation_split=0.4,
                        shuffle=True
                        )
  model_m.save("model/DummyTestModel_last.h5")
  return jsonify({"message":"Model saved succesfully!"})
  

def cycle_detector(year,month, day , Resolution, window_size):
  Feed= []
  df1 = load_DF ("Cycle",year,month,day)

  for i in range(0,len(df1['Cycle'])-window_size,Resolution):
    f = np.array(df1.iloc[i:i+window_size]['Cycle']).reshape(-1,1)
    Feed.append(f)
  day=np.array(Feed)
  

  model_m=load_model('model/DummyTestModel.h5')
  

  Y_predict2 = model_m.predict(day)
  peaks, _ = find_peaks(np.array(Y_predict2.reshape(-1)), height=1)
  XXX = np.array(peaks*Resolution).reshape(-1)
  YYY = Probability[peaks].reshape(-1)
  return (peaks*Resolution)

@app.route('/anomaly_train',methods=['GET'])
def anomaly_train():
  days,cycles,X,Y = [],[], [],[] 

  for i in range (1,12,1):
    df1 = load_DF ("Cycle","2020","1",str(i))
    df2 = load_DF ("Sensor","2020","1",str(i))
    A_Positive = df1[df1['Sts']==8].index
    for row in A_Positive:
      if row<(86400-3600):
        if df2.iloc[row]['anomaly']==8:
          cyc = np.array(df2.iloc[row+margin:row+window_size-margin]['sensor']).reshape(-1,1)
          X.append(cyc)
    days.append('2021-1-'+str(i))
  X = np.array(X)
  model = DeepAnt_Model()

  model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath='model/DummyAnomaly_Test.h5',
    monitor='val_loss',
    mode='min',
    patience = 90,
    save_best_only=True)

  history = model.fit(
    X,
    X,
    epochs=600,
    batch_size=4,
    validation_split=0.4,
    callbacks=[model_checkpoint_callback],
  )
  x_train_pred = model.predict(X)
  x_train_pred = x_train_pred.reshape(46,window_size-2*margin,1)
  train_mae_loss = np.mean(np.abs(x_train_pred - X), axis=1)
  threshold = np.max(train_mae_loss)
