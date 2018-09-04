import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import os
import pandas as pd
import plotly.graph_objs as go

from collections import Counter
from numpy import polyfit
from plotly import tools

import utils
from app import app
from apps import rep

tab = rep.Tab(
  label="Comparison", 
  value="comparison",
  dashboard=rep.Dashboard([
    rep.ShowsElement(elt_id="comp-shows"),
    rep.YearsElement(elt_id="comp-years"),
    rep.RaceElement(elt_id="comp-race")
  ]),
  panel=rep.Panel([
    html.H3("The Bachelor/ette is still less diverse than the U.S. at large"),
    dcc.Graph(id="comparison-graph"),
    html.H4("Some text")
  ])
)

@app.callback(
  Output("comparison-graph", "figure"),
  [Input(input_id, "value") for input_id in 
    ["comp-shows", "comp-years", "comp-race"] ]
)
def update_graph(shows, years, race):
  filtered_df = rep.get_filtered_df(leads=[False], shows=shows, years=years)
  traces = []
  layout = go.Layout()
  return dict(data=traces, layout=layout)

@app.callback(
  Output("selected-comp-years", "children"),
  [Input("comp-years", "value")])
def update_years(years):
  return rep.update_selected_years(years)