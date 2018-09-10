import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import plotly.graph_objs as go
from collections import Counter

import utils
from app import app
from apps import perf

# How likely is it for a POC candidate to be in the 1st week vs. 
# a white candidate

tab = utils.Tab(
  label="Initial", 
  value="initial", 
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id="initial-shows"),
    utils.YearsElement(elt_id="initial-years"),
    utils.RaceElement(elt_id="initial-race")
  ]),
  panel=utils.Panel([
    html.H4("POC candidates are slightly more likely to be eliminated Week 1"),
    dcc.Graph(id="initial-graph"),
    html.Br(),
    html.H5([
      "POC candidates have approximately the same chance as white ",
      "candidates of leaving the show on week one - without much substantial ",
      "time to explore a relationship with the show's lead.",
      html.Br(), html.Br(),
      "Asian & Pacific Islander contestants as a group are disproportionately ",
      "likely to leave the show early, whereas mixed ethnicity contestants ",
      "tend to avoid an early departure."])
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

def get_perc_val(first_week_counts, total_counts, val):
  total = total_counts.get(val)
  if total == 0:
    return 0
  return 100 * float(first_week_counts.get(val)) / total

@app.callback(
  Output("initial-graph", "figure"),
  [Input("initial-{}".format(stub), "value") for stub in 
    ["shows", "years", "race"] ]
)
def update_graph(shows, years, race):
  df = perf.get_filtered_df([True, False], shows, years)

  start, end = years
  layout = go.Layout(
    title="Percentage Candidates Eliminated First Week<br>{}-{}".format(start, end),
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
    x = {}
    for show in shows:
      df_show = df[df.show == show]
      for season in df_show.season.unique():
        season_df = df_show[df_show.season == season]
        total_counts = Counter(season_df["poc_flag"])
        fw_counts = Counter(season_df[season_df.num_weels == 1]["poc_flag"])
        for val in x_vals:
          title = perf.get_poc_name(val)
          p_elim = get_perc_val(fw_counts, total_counts, val)
          x[title] = x.get(val, []) + [p_elim]

    total_counts = Counter(df["poc_flag"])
    first_week_counts = Counter(df[df.num_weeks == 1]["poc_flag"]) 
    x_vals = [False, True]
    x = []
    for val in x_vals:
      title = perf.get_poc_name(val)
      p_fweek_elim = get_perc_val(first_week_counts, total_counts, val)
      x.append(title)
      y.append(p_fweek_elim)
      colors.append(utils.get_race_color(title))
    bar = get_bar(x, y, colors)
  
  elif race == "all":
    counts = df.count()
    total_counts = {flag: int(counts[flag]) for flag in utils.RACE_TITLES.keys()}
    fw_counts = df[df.num_weeks == 1].count()
    first_week_counts = {flag: int(fw_counts[flag]) for flag in 
      utils.RACE_TITLES.keys()}
    x = []
    for val, title in utils.RACE_TITLES.items():
      p_fweek_elim = get_perc_val(first_week_counts, total_counts, val)
      x.append(title)
      y.append(p_fweek_elim)
      colors.append(utils.get_race_color(val))
    bar = get_bar(x, y, colors)

  return dict(data=[bar], layout=layout)

@app.callback(
  Output("selected-initial-years", "children"),
  [Input("initial-years", "value")])
def update_years(years):
  return utils.update_selected_years(years)