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

def get_poc_name(x):
  return {True: "POC", False: "White"}[x]

def get_lead_name(x):
  return {True: "Bachelor/ettes", "true": "Bachelor/ettes", 
          False: "Contestants", "false": "Contestants"}[x]

def get_yearly_data(df, flag_name, flag_value, get_dict=False):
  """returns the % times a flag is equal to a value, for all years in df """
  group_vals = df[flag_name].groupby(df["year"])
  x, y = [], []
  for year, vals in group_vals:
    counter = Counter(vals)
    total = sum(counter.values())
    # if flag val isn't in counter, it appeared 0 times
    num_flag = counter.get(flag_value, 0)
    perc_flag = round((float(num_flag)/total) * 100, 2)
    y.append(perc_flag)
    x.append(year)
  if get_dict:
    return dict(zip(x, y))
  return x, y

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