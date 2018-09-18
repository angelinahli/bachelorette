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

tab = dcc.Tab(label="Overall", value="overall")

content = utils.TabContent(
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
      """
      While overall, POC candidates exit from the Bachelor/ette earlier in
      a shows' run than their non-POC counterparts, this difference is
      minimal in magnitude.
      """, 
      html.Br(), html.Br(),
      """
      In fact, some populations of non-white candidates appear to outcompete
      their white peers; more data would be required to determine if this
      difference is significant.
      """]),
    html.H6(id=stub + "caption", className="caption")
  ])
)

@app.callback(
  Output(stub + "graph", "figure"),
  [Input(stub + inp, "value") for inp in ["shows", "years", "race"] ]
)
def update_graph(shows, years, race):
  if not race:
    return dict(data=[], layout=go.Layout())
  
  data = dict(x=None, y=[], colors=[])
  filtered_df = perf.get_filtered_df(shows, years)
  title_dict = utils.POC_TITLES if race == "poc_flag" else utils.RACE_TITLES
  x_vals = utils.get_ordered_race_flags(title_dict.keys())
  for flag in x_vals:
      series = filtered_df[filtered_df[flag] == 1].perc_weeks
      data["colors"].append(utils.get_race_color(flag))
      data["y"].append(round(series.mean() * 100, 1))
  data["x"] = list(map(title_dict.get, x_vals))
  
  start, end = years
  layout = go.Layout(
    title="Average Percentage of Season Candidates Last<br>{}-{}".format(
      start, end),
    xaxis=dict(tickfont=dict(size=14)),
    margin=dict(b=120 if race == "all" else 50),
    **utils.LAYOUT_ALL)
  bar = utils.Bar(text=data["y"], **data)
  layout.update(yaxis=dict(range=[0, max(bar.get("y", [0])) + 5]))
  return dict(data=[bar], layout=layout)

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)