import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import plotly.graph_objs as go
from collections import Counter

import utils
from app import app
from apps import perf

# Average percentage of time on the show by racial category, by POC lead or not

tab = utils.Tab(
  label="Overall", 
  value="overall", 
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id="overall-perf-shows"),
    utils.YearsElement(elt_id="overall-perf-years"),
    utils.RaceElement(elt_id="overall-perf-race")
  ]),
  panel=utils.Panel([
    html.H4("POC do about as well as non-POC candidates on average"),
    dcc.Graph(id="overall-perf-graph"),
    html.Br(),
    html.H5("Some more text about this"),
    html.H6(id="overall-perf-caption", className="caption")
  ])
)

def get_mean_pweeks(df, race_flag, race_value):
  new_df = df[df[race_flag] == race_value]
  return round(new_df.perc_weeks.mean() * 100, 2)

def get_std_pweeks(df, race_flag, race_value):
  return df[df[race_flag] == race_value].perc_weeks.std() * 100

def get_bar(x, y, stds, colors):
  return go.Bar(
    x=x,
    y=y,
    error_y=dict(
      type="data", 
      array=stds, 
      thickness=1, 
      color=utils.SECONDARY_COLOR,
      visible=True),
    hoverinfo="x+y",
    marker=dict(color=colors)
  )

@app.callback(
  Output("overall-perf-graph", "figure"),
  [Input("overall-perf-{}".format(stub), "value") for stub in 
    ["shows", "years", "race"] ]
)
def update_graph(shows, years, race):
  filtered_df = perf.get_filtered_df([True, False], shows, years)
  start, end = years
  layout = go.Layout(
    title="Percentage of Season Candidates Last<br>{}-{}".format(start, end),
    xaxis=dict(tickfont=dict(size=14)),
    legend=dict(orientation="h"),
    hovermode="closest",
    margin=dict(b=100),
    **utils.LAYOUT_FONT
  )

  traces = []

  if race == "poc_flag":
    x_vals = [False, True]
    x = list(map(perf.get_poc_name, x_vals))
    y = []
    stds = []
    colors = []
    for i in range(len(x_vals)):
      y.append(get_mean_pweeks(filtered_df, "poc_flag", x_vals[i]))
      stds.append(get_std_pweeks(filtered_df, "poc_flag", x_vals[i]))
      colors.append(utils.get_race_color(x[i]))
    traces.append(get_bar(x, y, stds, colors))
  
  elif race == "all":
    x_vals = utils.get_ordered_race_flags(utils.RACE_TITLES.keys())
    x = list(map(lambda flag: utils.RACE_TITLES.get(flag), x_vals))
    y = []
    stds = []
    colors = []
    for flag in x_vals:
      y.append(get_mean_pweeks(filtered_df, flag, 1))
      stds.append(get_std_pweeks(filtered_df, flag, 1))
      colors.append(utils.get_race_color(flag))
    traces.append(get_bar(x, y, stds, colors))

  return dict(data=traces, layout=layout)

@app.callback(
  Output("selected-overall-perf-years", "children"),
  [Input("overall-perf-years", "value")])
def update_years(years):
  return utils.update_selected_years(years)