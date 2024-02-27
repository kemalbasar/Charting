import warnings
from datetime import date, timedelta, datetime
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, no_update, exceptions
import dash_bootstrap_components as dbc

from valfapp.configuration import layout_color
from valfapp.functions.functions_prd import scatter_plot, get_daily_qty, generate_for_sparkline, working_machinesf, indicator_with_color
from run.agent import ag
from valfapp.app import app, prdconf, return_piechart
from valfapp.layouts import nav_bar
from valfapp.pages.date_class import update_date, update_date_output
from config import kb
import tkinter as tk

layout = dbc.Container(className="body",children=[
    html.Div(className="container-fluid",  children=[
        html.Div(className="row justify-content-center align-items-center", children=[
            html.Div(className="col-lg-4 col-md-8 col-sm-12 mt-5", style={
                "height": "600px",
                "border-radius": "20px",
                "box-shadow": "1px 1px 10px #2149b5",
                "text-align": "center",
                "background-color":"white"
            }, children=[
                html.Img(src="../assets/valflogo.png", style={"width": "150px"}),

                html.Div(className="mt-5", children=[
                    html.Form(children=[
                        html.Div(className="email text-start", children=[
                            html.Label("Kullanıcı Adı:", className="fw-bold"),
                            html.Div(className="sec-2", children=[
                                dcc.Input(type="text", id="username" , placeholder="Örnek: valfsan")
                            ])
                            ])
                        ]),

                        html.Div(className="password mt-3 text-start", children=[
                            html.Label("Şifre:", className="fw-bold"),
                            html.Div(className="sec-2", children=[
                                dcc.Input(type="password", id="password", placeholder="············"),
                            ])
                        ]),

                        html.Button("Login" ,id="login-button", className="login mt-3 fw-bold")
                    ])
                ])
            ])
        ])
    ])

