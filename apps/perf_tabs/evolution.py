import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
from numpy import polyfit
from plotly import tools

import utils
from app import app
from apps import perf

stub = "evol-perf-"

tab = dcc.Tab(label="Evolution", value="evolution")

content = utils.TabContent(
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.H4("POC representation has improved over time"),
    dcc.Graph(id=stub + "graph"),
    html.H5([
      """
      In recent years, a higher number of people of color have
      participated in the Bachelor/ette.
      """,
      html.Br(), html.Br(),
      """
      Representation of POC contestants rose sharply after two rejected
      applicants filed a racial discrimination lawsuit against the
      franchise in 2012.
      """])
  ])
)

def get_pweeks_data(df, year_start, year_end):
  group_vals = df["perc_weeks"].groupby(df["year"])
  x, y = [], []
  for year, vals in group_vals:
    x.append(year)
    y.append(round(vals.mean() * 100, 1))
  return x, y

def get_poc_fig(df, year_start, year_end, layout_all):
  layout = go.Layout(
    yaxis=dict(title="% Season", titlefont=dict(size=16)), 
    annotations=[],
    height=500,
    **layout_all
  )
  traces = []
  for flag in ["poc", "white"]:
    flag_df = df[df[flag] == 1]
    x, y = get_pweeks_data(flag_df, year_start, year_end)
    title = utils.POC_TITLES.get(flag)
    color = utils.get_race_color(flag)
    scatter = utils.Scatter(x=x, y=y, color=color, name=title, 
                            size=6, mode="lines")
    traces.append(scatter)
  return dict(data=traces, layout=layout)

def get_all_fig(df, year_start, year_end, layout_all):
  race_titles = dict(utils.RACE_TITLES)
  race_titles.pop("white")
  race_keys = utils.get_ordered_race_flags(race_titles.keys())

  rows, cols = 3, 2
  order = [(r, c) for r in range(1, rows + 1) for c in range(1, cols + 1)]
  trace_pos = dict(zip(race_keys, order))

  fig = tools.make_subplots(
    rows=rows, cols=cols, 
    vertical_spacing = 0.1,
    subplot_titles=tuple(race_titles.get(k) for k in race_keys) )

  # new subplot per racial category
  axis_num = 1
  all_y = []
  for flag in race_keys:
    flag_df = df[df[flag] == 1]
    xaxis = "xaxis{}".format(axis_num)
    yaxis = "yaxis{}".format(axis_num)
    color = utils.get_race_color(flag)
    row, col = trace_pos.get(flag)
    title = race_titles.get(flag)

    x, y = get_pweeks_data(flag_df, year_start, year_end)
    scatter = utils.Scatter(x=x, y=y, color=color, name=title, 
                            xaxis=xaxis, yaxis=yaxis, size=6, mode="lines")
    fig.append_trace(scatter, row, col)
    all_y += y
    fig["layout"].update({yaxis: dict(title="% Season")})
    axis_num += 1

  min_y = min(0, min(all_y))
  max_y = max(all_y)
  inc = (max_y - min_y)/11.0
  for num in range(1, axis_num):
    fig["layout"]["yaxis{}".format(num)].update(range=[min_y - inc, max_y + inc])

  fig["layout"].update(height=300*rows, showlegend=False, **layout_all)
  return fig

@app.callback(
  Output(stub + "graph", "figure"),
  [Input(input_id, "value") for input_id in 
    [stub + "shows", stub + "years", stub + "race"] ]
)
def update_graph(shows, years, race):
  df = perf.get_filtered_df(shows, years)
  start, end = years

  layout_all = dict(
    title="Average Percentage of a Season Candidates Last" \
      + "<br>{}-{}".format(start, end),
    **utils.LAYOUT_ALL)

  if race == "poc_flag":
    return get_poc_fig(df, start, end, layout_all)
  elif race == "all":
    return get_all_fig(df, start, end, layout_all)
  return dict(data=[], layout=go.Layout())

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)