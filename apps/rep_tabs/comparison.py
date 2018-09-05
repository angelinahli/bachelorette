import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import os
import pandas as pd
import plotly.graph_objs as go

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

def get_trace(mast_vals, census_df, cen_flag, title, color):

  cen_vals = dict(zip(census_df.year, census_df[cen_flag + "_perc"]))
  common_years = list(filter(lambda year: year in mast_vals.keys(), cen_vals))
  perc_diffs = [mast_vals.get(yr) - (cen_vals.get(yr)*100) for yr in common_years]
  return go.Bar(
    x=common_years, y=perc_diffs,
    hoverinfo="x+y",
    marker=dict(color=color),
    name=title)

@app.callback(
  Output("comparison-graph", "figure"),
  [Input(input_id, "value") for input_id in 
    ["comp-shows", "comp-years", "comp-race"] ]
)
def update_graph(shows, years, race):
  filtered_df = rep.get_filtered_df(leads=[False], shows=shows, years=years)
  census_df = rep.census[rep.census.year.isin(filtered_df.year.unique())]
  layout = go.Layout()
  traces = []

  if race == "all":
    colors = utils.get_colors(rep.race_titles.keys())
    for flag, title in rep.race_titles.items():
      mast_vals = rep.get_yearly_data(filtered_df, flag, 1, get_dict=True)
      color = colors.get(flag)
      trace = get_trace(mast_vals, census_df, flag, title, color)
      traces.append(trace)
            
  elif race == "poc_flag":
    crosswalks = [("nwhite", True), ("white", False)]
    colors = utils.get_colors([True, False])
    for cen_flag, mast_val in crosswalks:
      mast_vals = rep.get_yearly_data(filtered_df, "poc_flag", mast_val, 
                                      get_dict=True)
      title = rep.get_poc_name(mast_val)
      color = colors.get(mast_val)
      trace = get_trace(mast_vals, census_df, cen_flag, title, color)
      traces.append(trace)
    
  return dict(data=traces, layout=layout)

@app.callback(
  Output("selected-comp-years", "children"),
  [Input("comp-years", "value")])
def update_years(years):
  return rep.update_selected_years(years)