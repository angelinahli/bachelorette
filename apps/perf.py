import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import os
import pandas as pd
from collections import Counter

import utils
from app import app

########## importing in data ##########

work_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(work_dir, "..", "data", "master_flags_dataset.csv"))

########## helper functions ##########

def get_filtered_df(shows, years):
  start, end = years
  return df[
    (df["lead_flag"] == 0)
    & (df["show"].isin(shows))
    & (df["year"] >= start)
    & (df["year"] <= end)
  ]

def get_lead_race_name(x):
  return {True: "POC Lead", False: "White Lead"}[x]

########## main content ##########

# place here to avoid circular imports
from apps.perf_tabs import overall, winners

title = "Part 2: How well do POC Bachelor/ette contestants fare on the show?"
subtitle = "POC contestants stick around but almost never win."

main_content = html.Div([
  utils.Tabs(
    id="perf-tabs",
    value="overall",
    children=[overall.tab, winners.tab]),
  html.Div(id="perf-content")
])

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)

########## route to display tab content ##########

@app.callback(Output("perf-content", "children"), [Input("perf-tabs", "value")])
def render_tab_content(tab_val):
  tab_values = {
    "overall": overall.content,
    "winners": winners.content
  }
  return tab_values.get(tab_val)