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

"""
Brainstorm:
* Average number of weeks on the show by racial category, by POC lead or not
* Change in average number of weeks by race
"""

########## helper functions ##########

def get_filtered_df(lead_race, shows, years):
  start, end = years
  return df[
    (df["lead_flag"] == 0)
    & (df["lead_poc_flag"].isin(lead_race))
    & (df["show"].isin(shows))
    & (df["year"] >= start)
    & (df["year"] <= end)
  ]

def get_lead_race_name(x):
  return {True: "POC Lead", False: "White Lead"}[x]

def get_poc_name(x):
  return {True: "POC", False: "White"}[x]

########## defining dashboard elements ##########

class LeadRaceElement(utils.FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Lead's Race",
      element=dcc.Dropdown(
        id=elt_id,
        options=[
          {"label": "POC Lead", "value": True}, 
          {"label": "White Lead", "value": False}
        ],
        value=[True, False],
        multi=True
      ))

########## main content ##########

# place here to avoid circular imports
from apps.perf_tabs import overall, initial

title = "Part 2: How well do POC Bachelor/ette contestants fare on the show?"
subtitle = "Not great."

main_content = utils.Tabs(
  value="overall",
  children=[overall.tab, initial.tab])

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)