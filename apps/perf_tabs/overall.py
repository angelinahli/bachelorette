import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
from collections import Counter
from scipy import stats

import utils
from app import app
from apps import perf

# Average percentage of time on the show by racial category

tab = utils.Tab(
  label="Overall", 
  value="overall", 
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id="overall-perf-shows"),
    utils.YearsElement(elt_id="overall-perf-years"),
    utils.RaceElement(elt_id="overall-perf-race")
  ]),
  panel=utils.Panel([
    html.H4("POC candidates do almost as well as non-POC candidates overall"),
    dcc.Graph(id="overall-perf-graph"),
    html.Br(),
    html.H5([
      "While overall, POC candidates exit from the Bachelor/ette earlier in ",
      "a shows' run than their non-POC counterparts, this difference is ",
      "minimal in magnitude.", 
      html.Br(), html.Br(),
      "In fact, some populations of non-white candidates appear to outcompete ",
      "their white peers; more data would be required to determine if this ",
      "difference is significant."]),
    html.H6(
      children=[
        "The average percentage of time that POC and white candidates ",
        "spend on the show is statistically difference at the p = 0.05 level."], 
      className="caption")
  ])
)

def get_bar(x, y, colors):
  return go.Bar(
    x=x,
    y=y,
    text=y,
    textposition="outside",
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
    margin=dict(b=120, t=-10),
    **utils.LAYOUT_FONT
  )
  y = []
  colors = []
  bar = None
  
  if race == "poc_flag":
    x_vals = [False, True]
    x = list(map(perf.get_poc_name, x_vals))
    y_series = []
    for i in range(len(x_vals)):
      series = filtered_df[filtered_df["poc_flag"] == x_vals[i]].perc_weeks
      y.append(round(series.mean() * 100, 2))
      colors.append(utils.get_race_color(x[i]))
      y_series.append(series)
    bar = get_bar(x, y, colors)
    pvalue = round(stats.ttest_ind(*y_series, equal_var=False).pvalue, 4)
    layout["xaxis"].update(title="p value: {}".format(pvalue))
  
  elif race == "all":
    x_vals = utils.get_ordered_race_flags(utils.RACE_TITLES.keys())
    x = list(map(lambda flag: utils.RACE_TITLES.get(flag), x_vals))
    for flag in x_vals:
      series = filtered_df[filtered_df[flag] == 1].perc_weeks
      y.append(round(series.mean() * 100, 2))
      colors.append(utils.get_race_color(flag))
    bar = get_bar(x, y, colors)
  
  return dict(data=[bar], layout=layout)

@app.callback(
  Output("selected-overall-perf-years", "children"),
  [Input("overall-perf-years", "value")])
def update_years(years):
  return utils.update_selected_years(years)