import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import numpy as np
import plotly.graph_objs as go
from collections import Counter

import utils
from app import app
from apps import perf

stub = "over-perf-"

tab = utils.Tab(
  label="Overall", 
  value="overall", 
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.Div(id=stub + "value", style=dict(display="none")),
    html.H4("POC candidates do almost as well as non-POC candidates overall"),
    dcc.Graph(id=stub + "graph"),
    html.Br(),
    html.H5([
      "While overall, POC candidates exit from the Bachelor/ette earlier in ",
      "a shows' run than their non-POC counterparts, this difference is ",
      "minimal in magnitude.", 
      html.Br(), html.Br(),
      "In fact, some populations of non-white candidates appear to outcompete ",
      "their white peers; more data would be required to determine if this ",
      "difference is significant."]),
    html.H6(id=stub + "caption", className="caption")
  ])
)

def get_perm_p_val(y_white, y_poc):
  mean_diff = np.mean(y_white) - np.mean(y_poc)
  num_trials = 2000
  all_y = y_white + y_poc
  diff_vals = []
  num_white = len(y_white)
  for _ in range(num_trials):
    np.random.shuffle(all_y)
    mean_white = np.mean(all_y[:num_white])
    mean_poc = np.mean(all_y[num_white:])
    diff_vals.append(mean_white - mean_poc)
  num_diff = len([d for d in diff_vals if d >= mean_diff])
  return round(float(num_diff) / num_trials, 2)

@app.callback(
  Output(stub + "value", "children"),
  [Input(stub + inp, "value") for inp in ["shows", "years", "race"] ]
)
def clean_data(shows, years, race):
  filtered_df = perf.get_filtered_df(shows, years)
  data = dict(x=None, y=[], colors=[])
  
  if race == "poc_flag":
    x_vals = [False, True]
    data["x"] = list(map(perf.get_poc_name, x_vals))
    y_series = []
    for i in range(len(x_vals)):
      series = filtered_df[filtered_df["poc_flag"] == x_vals[i]].perc_weeks
      data["colors"].append(utils.get_race_color( data["x"][i]) )
      data["y"].append(round(series.mean() * 100, 1))
      y_series.append(series.tolist())
    data["p_val"] = get_perm_p_val(*y_series)
  
  elif race == "all":
    x_vals = utils.get_ordered_race_flags(utils.RACE_TITLES.keys())
    data["x"] = list(map(lambda flag: utils.RACE_TITLES.get(flag), x_vals))
    for flag in x_vals:
      series = filtered_df[filtered_df[flag] == 1].perc_weeks
      data["colors"].append(utils.get_race_color(flag))
      data["y"].append(round(series.mean() * 100, 1))
  return json.dumps(data)

@app.callback(
  Output(stub + "graph", "figure"),
  [Input(stub + "value", "children"), Input(stub + "years", "value") ]
)
def update_graph(cleaned_data, years):
  data = json.loads(cleaned_data)
  if not data:
    return dict(data=[], layout=go.Layout())
  
  start, end = years
  layout = go.Layout(
    title="Percentage of Season Candidates Last<br>{}-{}".format(start, end),
    margin=dict(b=110),
    xaxis=dict(tickfont=dict(size=14)),
    **utils.LAYOUT_ALL)
  bar = utils.Bar(text=data["y"], **data)
  layout.update(yaxis=dict(range=[0, max(bar.get("y", [0])) + 5]))
  return dict(data=[bar], layout=layout)

@app.callback(
  Output(stub + "caption", "children"), 
  [Input(stub + "value", "children"), Input(stub + "race", "value")]
)
def get_caption(cleaned_data, race):
  data = json.loads(cleaned_data)
  if race == "poc_flag":
    cap = "The probability that POC candidates last as long as white " \
          + "contestants"

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)