from flask import Flask, request, send_file,redirect, url_for
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output
from datetime import datetime as dt
import numpy as np
import plotly.graph_objs as go
import os, requests, dash



header = dbc.Row([
  dbc.Col(md=2, children = [
    html.Img(src="assets/industry4.jpg", height="150px")
    ]),
  dbc.Col(md=10, style ={"margin-top": "70px"}, children = [
    html.H1('Anomaly Detector Dashboard')
    ]),
  ])
navbar = dbc.Nav(className="nav nav-pills", children=[
    ## logo/home
    ## about
    dbc.NavItem(html.Div([
        dbc.NavLink("About", href="/", id="about-popover", active=False),
        dbc.Popover(id="about", is_open=False, target="about-popover", children=[
            dbc.PopoverHeader("How it works")])
    ])),
    ## links
    dbc.DropdownMenu(label="Links", nav=True, children=[
        dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"), "  Contacts"], href="#", target="_blank"), 
        dbc.DropdownMenuItem([html.I(className="fa fa-github"), "  Code"], href="#", target="_blank")
    ]),
    dbc.NavItem(
      html.Div([
          html.Div([
            dcc.DatePickerSingle(
                  id='date-picker',
                  min_date_allowed=dt(2020, 9, 5),
                  max_date_allowed=dt(2021, 2,1),
                  initial_visible_month=dt(2021, 1, 1),
                  date=dt(2021, 1, 12, 23, 59, 59),
              )]),
        ])
    )    
])

