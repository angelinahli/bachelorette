import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
from numpy import polyfit
from plotly import tools

import utils
from app import app
from apps import rep

tab = rep.Tab(
  label="Evolution", 
  value="evolution",
  dashboard=rep.Dashboard([
    rep.ShowsElement(elt_id="evol-shows"),
    rep.YearsElement(elt_id="evol-years"),
    rep.RaceElement(elt_id="evol-race")
  ]),
  panel=rep.Panel([
    html.H4("POC representation has improved over time"),
    dcc.Graph(id="evol-graph"),
    html.H5("In recent years, a higher number of people of color are " \
      + "participating in the Bachelor/ette."),
    html.H6(id="evol-caption", className="caption")
  ])
)

captions = {
  "poc_flag": "Representation of POC contestants rose sharply after two " \
    + "rejected applicants filed a racial discrimination lawsuit against " \
    + "the franchise in 2012.",
  "all": "Some racial groups have seen much larger increases in " \
    + "representation than others."
  }

def get_scatter(x, y, color, name, **kwargs):
  return go.Scatter(
    x=x, y=y,
    hoverinfo="x+y",
    marker=dict(color=color, size=8),
    name=name,
    mode="markers",
    **kwargs)

def get_reg(x, y, beta_1, beta_0, color, name, **kwargs):
  text = ["" for _ in range(len(x) - 1)]
  text.append( u"β1 = {}".format(round(beta_1, 2)) )
  text_position = "top left" if beta_1 >= 0 else "bottom left"
  return go.Scatter(
    x=x,
    y=list(map(lambda x_val: beta_0 + (beta_1 * x_val), x)),
    text=text,
    textposition=text_position,
    textfont=dict(color=utils.SECONDARY_COLOR, size=13, family="Karla"),
    hoverinfo="x+y",
    marker=dict(color=color, size=2),
    name=name,
    mode="lines+text",
    **kwargs)

def get_poc_fig(df, layout_all):
  layout = go.Layout(
    yaxis=dict(title="% Candidates", titlefont=dict(size=16)), 
    legend=dict(orientation="h"),
    height=550,
    annotations=[],
    **layout_all
  )
  traces = []
  x, y = rep.get_yearly_data(df, "poc_flag", True)
  b1, b0 = polyfit(x, y, 1)
  color = utils.get_race_color("POC")
  traces.append(get_scatter(x, y, color, "Values"))
  traces.append(get_reg(x, y, b1, b0, color, "OLS Estimates"))
  
  if 2012 in x:
    increment = float(max(y) - min(y))/20 or 0.1
    layout["shapes"] = [
      dict(
        x0=2012, x1=2012, y0=min(y), y1=max(y), 
        type="line",
        line=dict(color=utils.SECONDARY_COLOR, width=2, dash="dot")
      )]
    layout["annotations"].append(
      dict(
        x=2012, y=max(y) + increment, 
        text="Discrimination<br>lawsuit", 
        **utils.LAYOUT_ANN)
    )
  return dict(data=traces, layout=layout)

def get_all_fig(df, layout_all):
  race_titles = dict(utils.RACE_TITLES)
  race_titles.pop("white")
  race_keys = utils.get_ordered_race_flags(race_titles.keys())

  rows, cols = 3, 2
  order = [(r, c) for r in range(1, rows + 1) for c in range(1, cols + 1)]
  trace_pos = dict(zip(race_keys, order))

  fig = tools.make_subplots(
    rows=rows, cols=cols, 
    subplot_titles=tuple(race_titles.get(k) for k in race_keys) )

  # new subplot per racial category
  i = 1
  for flag in race_keys:
    xaxis = "xaxis{}".format(i)
    yaxis = "yaxis{}".format(i)
    color = utils.get_race_color(flag)
    row, col = trace_pos.get(flag)
    title = race_titles.get(flag)

    x, y = rep.get_yearly_data(df, flag, 1)
    b1, b0 = polyfit(x, y, 1)
    scatter = get_scatter(x, y, color, title, xaxis=xaxis, yaxis=yaxis)
    reg = get_reg(x, y, b1, b0, color, title)

    fig.append_trace(scatter, row, col)
    fig.append_trace(reg, row, col)

    fig["layout"].update( 
      {xaxis: dict(title="Year"), yaxis: dict(title="% Candidates")} )
    i += 1

  fig["layout"].update(height=400*rows, showlegend=False, **layout_all)
  return fig

@app.callback(
  Output("evol-graph", "figure"),
  [Input(input_id, "value") for input_id in 
    ["evol-shows", "evol-years", "evol-race"] ]
)
def update_graph(shows, years, race):
  df = rep.get_filtered_df([False], shows, years)

  start, end = years
  layout_all = dict(
    title="Percentage POC Bachelor/ette Contestants<br>{}-{}".format(start, end),
    hovermode="closest",
    **utils.LAYOUT_FONT)

  if race == "poc_flag":
    return get_poc_fig(df, layout_all)
  elif race == "all":
    return get_all_fig(df, layout_all)
  return dict(data=[], layout=go.Layout())

@app.callback(Output("evol-caption", "children"), [Input("evol-race", "value")])
def update_caption(race):
  return captions.get(race)

@app.callback(
  Output("selected-evol-years", "children"),
  [Input("evol-years", "value")])
def update_years(years):
  return rep.update_selected_years(years)