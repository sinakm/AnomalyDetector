from flask import Flask, request, send_file,redirect, url_for
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output
from datetime import datetime as dt
import numpy as np
import plotly.graph_objs as go
import os, requests, dash, dash_table,datetime
from navbar import navbar, header


def time_margin(timestamp,increment):
  timestamp_Adj = dt.strptime(timestamp, '%H:%M:%S') + datetime.timedelta(seconds=increment)
  return (dt.strftime(timestamp_Adj,"%H:%M:%S"))

def timeChecker(df,timestamps):
  time_window = []
  for timestamp in timestamps:
    if len(df[df['Time']==time_margin(timestamp,0)])!=0:
      time_window.append(df.index[df['Time'] == time_margin(timestamp,0)].tolist()[0])
    else:
      time_window.append(df.index[df['Time'] == time_margin(timestamp,-1)].tolist()[0])
  return (time_window)




def staticGraphs(dates,graphid, title, axis1,axis1Title, axis2, axis2Title, csswidth, l,r,t,b):
    layoutStaticGraph = html.Div([
        html.H4(title),   
        dcc.Graph(id=graphid,
            figure = {
              'data': [
                  {'x': dates, 
                  'y': axis1, 
                  'type': 'scatter', 'name': axis1Title,
                  'marker' : { "color" : 'black'}}, 
                  {'x': dates, 
                  'y': axis2, 
                  'type': 'scatter', 'name': axis2Title,
                  'marker' : { "color" : 'red'}},                     
              ],
              'layout': dict(
                legend = dict(
                    font=dict(color='#7f7f7f'), 
                    orientabottomtion="v", # Looks much better horizontal than vertical
                    orientation= "v",
                    xanchor = "right",
                    ynchor = "bottom",
                    x = 1,
                    y = 1.02
                ),
                margin = dict(
                  l = l,
                  r = r,
                  t = t,
                  b = b,

                  )

                ),                      
            }, style = {'border':'2px solid',
                  'color': 'rgba(200,200,200,1)',
                  'margin': '10px',  
                  'padding':'0px',                  
              }
        )
    ], className=str(csswidth), style = {"border":"1px solid black", "background-color":"rgba(220,220,220,0.8)","margin-right":"10px"})

    return (layoutStaticGraph)



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'assets/dashboard.css',
                        'https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha1/css/bootstrap.min.css',

]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])


app.layout = dbc.Container(fluid=True, children=[
    ## Top
    header,
    html.Br(),html.Br(), 
    navbar, html.Br(),html.Br(),
    ## Body
    dbc.Row([
        ### input + panel
        dbc.Col(md=1, children=[]),
        ### plots
        dbc.Col(md=7, children=[
            dbc.Row([
              dbc.Col(html.H4('Daily Molding Cycle Detector'), width={"size":6, "offset":1}),
              dbc.Col(html.A('Download Labelled Dataset', href = "/download", id='download', className="btn btn-primary", style={'width':'300px;', 'float':'right'})),
              dbc.Col(html.A('Download Pump Predictions', href = "/dailyPrediction", id='dailyPrediction', className="btn btn-success", style={'width':'300px;', 'float':'right'})),
            ]),
            dbc.Tabs(className="nav nav-pills", children=[
                dbc.Tab(staticGraphs([],'Cycle','Production Cycles', [],'Buffer Pressure (bar)', [], 'Molding Cycles', 'col-md-12 col-sm-12', 1,1,1,1), label="Equipment 1"),
            ]),

            html.Br(), html.Br(),
            dbc.Row(className= "col-md-12", style = {'margin':'0','padding':'0'}, children = [ 
              staticGraphs([],'DosingPump','Dosing Pump Movements (Resin and Hardener)', [],'Resin (mm)', [], 'Hardener (mm)', 'col-md-12', 10,10,10,10),
              dbc.Col(className="col-md-1"),
              #staticGraphs([1,2,3,4,5,6,8,10,12,15],'DosingPump1','Resin vs Hardener Pumping Ratio', [2,4,0,8,0,-2,3,4,5],'Buffer Pressure (bar)', [10,11,0,12,10,2,3,4,5], 'Molding Cycles', 'col-md-5', 30,30,30,30)
              ])
        ]),
        dbc.Col(md=3, children=[]), 
        dbc.Col(md=1, children=[]),       
    ])
])

@app.callback(
  #Output('Anomaly','figure'),
  Output('Cycle','figure'),
  #Output(component_id = 'table_log',component_property = 'data'),
  Input('date-picker','date')

)
def update_graphs(selected_date):
  year = selected_date[0:4]
  month = selected_date[5:7]
  day = selected_date[8:10]

  if selected_date[5]=="0":
    month = selected_date[6]
  if selected_date[8]=="0":
    day = selected_date[9] 

  RawData_URL = 'http://172.20.0.1:7770/Cycle/fetch_data'
  JSONReq = {
    'year': year,
    'month': month,
    'day': day,
  }
  response = requests.get(RawData_URL,json=JSONReq).json()
  df = pd.DataFrame(data = np.array(response['data']),columns = response['columns'])

  RawData_URL = 'http://172.20.0.1:7771/cycle_checker'  
  JSONReq = {
    'year': year,
    'month': month,
    'day': day,
  }
  response = requests.get(RawData_URL,json=JSONReq).json()
  cycles = response['cycles']
  print("response")
  fig1 =  {
    'layout': dict(
    legend = dict(
        font=dict(color='#7f7f7f'), 
        #orientabottomtion="v", # Looks much better horizontal than vertical
        orientation= "h",
        xanchor = "right",
        ynchor = "bottom",
        x = 1,
        y = -0.2
        ),
    margin = dict(
      l = 35,
      r = 35,
      t = 35,
      b = 35,
      ),
    ),   
    'data': [
      {
        'x': df['Time'], 
        'y': df['Cycle'], 
        'mode':'marker',
        'marker' : { "color" : 'red' }
      }, 
      {
        'x': df.iloc[cycles]['Time'].tolist(), 
        'y': [6] * len(cycles),
        'mode':'markers',
        'marker' : { "color" : 'blue' }
      },      
    ]
  }
  return fig1  
'''
@app.callback(
  Output(component_id = 'test1', component_property = 'figure'),
  Output(component_id = 'table_log',component_property = 'data'),
  [Input(component_id = 'date-picker',component_property = 'date')],
)
def update_figure(mold_date):
  if os.path.exists('download.csv'):
    os.remove('download.csv')
  print('1.---------------------------------------------------------')
  RawData_URL = "http://172.20.0.1:5002/daily/"
  cyclePredictor_URL = "http://172.20.0.1:5001/fastTrack"
  predictorRequest = {
    'year': mold_date[0:4],
    'month': mold_date[5:7],
    'day': mold_date[8:10],
  }  
  cycleTimes = requests.get(cyclePredictor_URL,json=predictorRequest).json()  
  print('2. Cycle times identified')
  response = {}
  content = {}
  RawDataRequest = {
    'year': mold_date[0:4],
    'month': mold_date[5:7],
    'day': mold_date[8:10],
    'BU8A1': [4],
    'BU8A2': [],
    'BU8A3': [],
    'PEK': [],
    'SM8A1': [],
    'SM8A2': [],
  }
  response = requests.get(RawData_URL,json=RawDataRequest).json()
  print('3. raw data loaded')  
  df = pd.DataFrame(data = np.array(response['data']),columns = response['columns'])
  #df.set_index('Time')
  cycleTimeinDF = cycleTimes['Results']
  print(cycleTimeinDF)
  cycleTimeinDFY = [5]*len(cycleTimeinDF)

  df_csv = df
  df_csv['label']=0
  for cycle in cycleTimes['data']:
    df_csv[df_csv['Time']==cycle]['label']=1

  df_csv.to_csv('download.csv',index=False)
  
  print(df_csv['Time'].head(480))

  print('4. File Saved')
  print ('Indexes Detected:')
  print(cycleTimes['Results'])
  print ('Timestamps Detected:')
  print(cycleTimeinDFY)
  #label = 6*df_csv['label']
  #print(label)
  #del df_csv
  fig =  {
  'layout': dict(
    legend = dict(
        font=dict(color='#7f7f7f'), 
        #orientabottomtion="v", # Looks much better horizontal than vertical
        orientation= "h",
        xanchor = "right",
        ynchor = "bottom",
        x = 1,
        y = -0.2
        ),
    margin = dict(
      l = 35,
      r = 35,
      t = 35,
      b = 35,
      ),
    ),   
    'data': [
      {
        'x': df['Time'], 
        'y': df['BU8A1_4'], 
        'type': 'scatter', 'name': 'BU8A1_4',
        'marker' : { "color" : 'black'}
      }, 
      {
        'x': cycleTimeinDF, 
        'y': cycleTimeinDFY,
        'type': 'scatter', 'name': mold_date,
        'mode':'markers',
        'marker' : { "color" : 'red' }
      },      
    ]
  }

  dg = pd.DataFrame()
  dg['Date']=[mold_date] * len(cycleTimeinDF)
  dg['Time']=cycleTimeinDF
  #dg['Cycle_index']=cycleTimes['Results']
  return fig,dg.to_dict('records')

















@app.server.route('/download',methods=['GET'])
def download():
  if os.path.exists('download.csv'):
    return send_file('download.csv',
      mimetype='text/csv',
      attachment_filename='download.csv',
      as_attachment=True)
  else:
    return redirect(url_for('/'))

@app.server.route('/dailyPrediction',methods=['GET'])
def dailyPrediction():
  if os.path.exists('dailyPrediction.csv'):
    return send_file('dailyPrediction.csv',
      mimetype='text/csv',
      attachment_filename='dailyPrediction.csv',
      as_attachment=True)
  else:
    return redirect(url_for('/'))
'''

if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=7000, debug=True)

