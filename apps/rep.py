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
census = pd.read_csv(os.path.join(work_dir, "..", "data", "census_race.csv"))

########## helper functions ##########

def get_filtered_df(lead, shows, years):
  start, end = years
  return df[
    (df["lead_flag"] == lead)
    & (df["show"].isin(shows))
    & (df["year"] >= start)
    & (df["year"] <= end)
  ]

def add_2012_lawsuit_annot(x, y, layout):
  if 2012 in x:
    increment = float(max(y) - min(y))/20 or 0.1
    layout["shapes"] = [
      dict(
        x0=2012, x1=2012, y0=min(y), y1=max(y), 
        type="line",
        line=dict(color=utils.COLORS.get("secondary"), width=2, dash="dot")
      )]
    layout["annotations"].append(
      dict(
        x=2012, y=max(y) + increment, 
        text="Discrimination<br>lawsuit", 
        **utils.LAYOUT_ANN)
    )

########## defining dashboard elements ##########

class LeadElement(utils.FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Cast Type",
      element=dcc.Dropdown(
        id=elt_id,
        options=[
          {"label": "Bachelor/ettes", "value": True}, 
          {"label": "Contestants", "value": False}
        ],
        value=False,
      ))

########## main content ##########

# place here to avoid circular imports
from apps.rep_tabs import overall, evolution, comparison

title = "Part 1: Does the Bachelor/ette have a representation problem?"
subtitle = "..Yes. And here are the numbers to prove it."

main_content = html.Div([
  utils.Tabs(
    id="rep-tabs",
    value="overall",
    children=[overall.tab, evolution.tab, comparison.tab]),
  html.Div(id="rep-content")
])

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)

########## route to display tab content ##########

@app.callback(Output("rep-content", "children"), [Input("rep-tabs", "value")])
def render_tab_content(tab_val):
  tab_values = {
    "overall": overall.content,
    "evolution": evolution.content,
    "comparison": comparison.content
  }
  return tab_values.get(tab_val)