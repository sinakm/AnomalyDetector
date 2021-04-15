from flask import Flask, request, send_file,redirect, url_for,jsonify
from datetime import datetime
from time import strftime
from time import gmtime
import numpy as np
import pandas as pd
from scipy.ndimage.interpolation import shift
import os, requests, random ,datetime, json, glob
from random import seed

app = Flask(__name__)


segment,Y = {},{}
segment['A'] = [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6]
segment['B'] = [0,0.5,1,1.5,2]
segment['C'] = [0,0.2,0.3,0.4,0.5,1,1.5,1.8,2]
segment['D'] = [0,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,2,2.2,2.4]

Y['A'] = [0,6,5,6,3,8,7,8,3,6,5,6,0]
Y['B'] = [0,4,3,4,0]
Y['C'] = [0,4,0,4,1,6,0,6,0]
Y['D'] = [0,0.5,0.6,0.65,0.67,0.67,0.65,0.6,0.5,0.5,0.45,0]


# Purpose of tsMaker is to interpolate the datapoints in-between minute timestamps of segment arrays and save the data in a form of Signal vs. timelapse (seconds) format
def tsMaker(segment,Y,label):
  segment = [element * 10 for element in segment]
  X = np.arange(0,segment[-1]*60,1)
  Ys = []
  for i in X:
    if random.random()<0.4:
      randterm = random.random()
    else:
      randterm = 0
    Yrand= np.interp(i/60,segment,Y)+randterm
    Ys.append((i,Yrand,label))
  df = pd.DataFrame(data = Ys)
  return (df)


@app.route('/generate_data/',methods=['GET'])
def generate_files():
    files = glob.glob('/Sensor/*')
    if len(files)>0:
      return jsonify({"message":"Training data is already generated. You can run /delete_dataset if you need to refresh the folder"})
    const = 1
    sample_days = 31
    df= pd.DataFrame()
    df1 = tsMaker(const*segment['A'],Y['A'],'A')
    df2 = tsMaker(const *segment['B'],Y['B'],'B')
    df3 = tsMaker(const *segment['C'],Y['C'],'C')
    df4 = tsMaker(const *segment['D'],Y['D'],'D')
    frames = [df1,df2,df3,df4]
    df = pd.concat(frames, ignore_index = True)
    df.columns = ['X','Y','label']
    Temp = {}
    Cycle_Length = len(df[df['label']=="A"]['Y'])
    Temp['A'] = [(Cycle_Length/2-abs(Cycle_Length/2-i))/(Cycle_Length/4) + 50 +((Cycle_Length/2-abs(Cycle_Length/2-i))/(Cycle_Length/2))*np.sin(i * np.pi/90) + random.random()/2 for i in range(0,len(df[df['label']=='A']),1)]
    Temp['AA'] = [(Cycle_Length/2-abs(Cycle_Length/2-i))/(Cycle_Length/4) + 50 +((Cycle_Length/2-abs(Cycle_Length/2-i))/10000)*np.sin(i * np.pi/10) + random.random()/20 for i in range(0,len(df[df['label']=='A']),1)]
    Temp['B'] = [50+np.sin(i * np.pi/90)/10+random.random()/20 for i in range(0,len(df[df['label']=='B']),1)]
    Temp['C'] = [40+np.sin(i * np.pi/10)/10+random.random()/20 for i in range(0,len(df[df['label']=='C']),1)]
    Temp['D'] = [45+np.sin(i * np.pi/10)/10+random.random()/20 for i in range(0,len(df[df['label']=='D']),1)]

    for i in range(1,sample_days,1):
      timeseries,sensor,status,labl,anomaly,anomalyTag,anomalyTagSeries = [],[],[],[],[],[],[]
      flag = False  
      Cycle_Log = pd.DataFrame ()
      Sensor_Log = pd.DataFrame ()  
      while flag == False:
        order = random.choice('ABCD')
        data = df[df['label']==order]['Y'].tolist()
        status = [0]*len(data)
        timeseries +=data
        anomalyTag = [0]*len(data)
        if (order !="A"):
          sensor +=Temp[order]
        else:
          status[0]=8
          anomaly = random.random()
          if anomaly >0.6:
            sensor +=Temp['AA']
          else:
            sensor +=Temp['A']
            anomalyTag[0]=8
        
        labl+=status
        anomalyTagSeries+=anomalyTag
        gap = [0]*random.randint(0,2000)
        if (86400-len(timeseries))>2000:
          gap = [0]*random.randint(0,2000)
        else:
          gap = [0]*(86400-len(timeseries))
          flag = True
        timeseries +=gap
        labl+=gap
        sensor +=gap
        anomalyTagSeries+=gap
        
      date = 86400*['2021-1-'+str(i)]
      filename1 = 'Cycle/2021-1-'+str(i)+'.csv'
      filename2 = 'Sensor/2021-1-'+str(i)+'.csv'
      time = [strftime("%H:%M:%S", gmtime(j)) for j in range(0,86400,1)]
      Cycle_Log['Date']=date
      Cycle_Log['Time']=time
      Cycle_Log['Cycle']=timeseries[0:86400]
      Cycle_Log['Sts']=labl[0:86400]
      Sensor_Log['Date']=date
      Sensor_Log['Time']=time
      Sensor_Log['sensor']=sensor[0:86400]
      Sensor_Log['anomaly']=anomalyTagSeries[0:86400]
      Cycle_Log.to_csv(filename1)
      Sensor_Log.to_csv(filename2)
    
    return jsonify({"message":"Data Generated Sucessfully"})




@app.route('/delete_dataset',methods = ['GET'])
def delete_dataset():
  files = glob.glob('/Sensor/*')
  for f in files:
      os.remove(f)
  files = glob.glob('/Cycle/*')
  for f in files:
      os.remove(f)

  return jsonify({"message":"The folders are cleaned up!"})


@app.route('/Cycle/fetch_data',methods=['GET'])
def Cycle_fetch():
  req=request.json
  df = pd.DataFrame ()
  filepath = 'Cycle/'+req['year']+'-'+req['month']+'-'+req['day']+'.csv'
  df = pd.read_csv(filepath)

  return (df.to_json(orient="split"))


@app.route('/Sensor/fetch_data',methods=['GET'])
def Sensor_fetch():
  req=request.json
  df = pd.DataFrame ()
  filepath = 'Sensor'+req['year']+'-'+req['month']+'-'+req['day']+'.csv'
  df = pd.read_csv(filepath)

  return (df.to_json(orient="split"))


@app.route('/fetch_data',methods=['GET'])
def fetch_data():
      return ("This route will return data from original dataset and pass it to other containers")



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=7000, debug=True)