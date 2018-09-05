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

########## data elements ##########

race_titles = {
  "white": "White",
  "afam": "African American",
  "amin": "Native American",
  "hisp": "Hispanic",
  "asn_paci": "Asian & Pacific Islander",
  "oth": "Other",
  "mult": "Multiple"
}

layout_font = dict(font=dict(family="Karla"))

########## helper functions ##########

def get_filtered_df(leads, shows, years, include_incomplete=True):
  start, end = years
  comp_vals = [True, False] if include_incomplete else [True]
  return df[
    (df["race_data_flag"] == True)
    & (df["show"].isin(shows))
    & (df["year"] >= start)
    & (df["year"] <= end)
    & (df["year_comp_flag"].isin(comp_vals))
  ]

def get_poc_name(x):
  return {True: "POC", False: "White"}[x]

def get_lead_name(x):
  return {True: "Leads", "true": "Leads", 
          False: "Contestants", "false": "Contestants"}[x]

def update_selected_years(years):
  """ shows user what the selected year range is """
  start, end = years
  return "Selected: ({start}, {end})".format(start=start, end=end)

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

########## helper classes ##########

class Tab(dcc.Tab):
  def __init__(self, dashboard=None, panel=None, **kwargs):
    super().__init__(**kwargs)
    self.children=html.Div(
      className="row", 
      children=[dashboard, panel]
    )

class Panel(html.Div):
  def __init__(self, children, **kwargs):
    super().__init__(
      className="col-sm-9 text-center", 
      children=[html.Br()] + children, 
      **kwargs)

class Dashboard(html.Div):
  def __init__(self, form_elements, **kwargs):
    super().__init__(className="col-sm-3", **kwargs)
    self.children = [
      html.Br(),
      html.H5("Change what this figure shows:"),
      html.Br()
    ]
    self.children += form_elements

########## defining dashboard elements ##########

class LeadsElement(utils.FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Contestants",
      element=dcc.Dropdown(
        id=elt_id,
        options=[
          {"label": "Leads", "value": True}, 
          {"label": "Contestants", "value": False}
        ],
        value=[True, False],
        multi=True
      ))

class ShowsElement(utils.FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Show(s)",
      element=dcc.Dropdown(
        id=elt_id,
        options=utils.get_form_options(["Bachelor", "Bachelorette"]),
        value=["Bachelor", "Bachelorette"],
        multi=True
      ))

class YearsElement(utils.FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Year(s)",
      element=dcc.RangeSlider(
        id=elt_id,
        min=2002,
        max=2018,
        step=1,
        marks={2002: 2002, 2010: 2010, 2018: 2018},
        value=[2002, 2018]
      ),
      add_elements=[
        html.Br(), 
        html.P(id="selected-" + elt_id, className="text-right small")
      ])

class RaceElement(utils.FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Comparison Specificity",
      element=dcc.Dropdown(
        id=elt_id,
        options=[
          {"label": "POC / Non-POC", "value": "poc_flag"},
          {"label": "All categories", "value": "all"}
        ],
        value="poc_flag"
      ))

########## main content ##########

# place here to avoid circular imports
from apps.rep_tabs import overall, evolution, comparison

title = "Part 1: Does the Bachelor/ette have a representation problem?"
subtitle = "..Yes. And here are the numbers to prove it."

main_content = html.Div(
  className="row",
  children=utils.Tabs(
  value="overall",
  children=[overall.tab, evolution.tab, comparison.tab])
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)