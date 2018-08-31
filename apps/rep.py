import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import os
import pandas as pd
from plotly import tools
import plotly.graph_objs as go
from collections import Counter

import utils
from app import app

########## importing in data ##########

work_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(work_dir, "..", "data", "master_flags_dataset.csv"))

########## defining main elements ##########

title = "Part 1: Does the Bachelor/ette have a representation problem?"
subtitle = "..Yes. And here are the numbers to prove it."

########## helper classes ##########

class MultiDropDown(dcc.Dropdown):
  def __init__(self, values, **kwargs):
    super().__init__(
      options=utils.get_form_options(values),
      value=list(values),
      multi=True,
      **kwargs)

class Tab(dcc.Tab):
  def __init__(self, children, **kwargs):
    super().__init__(**kwargs)
    self.children = [html.Br()] + children

########## designing general ui ##########

##### dashboard #####

dashboard = html.Div(
  className="col-sm-3",
  children=[
    html.H5("Change what this figure shows:"),
    html.Br(),
    utils.FormElement(
      label="Contestants",
      element=dcc.Dropdown(
        id="leads",
        options=[
          {"label": "Leads", "value": True}, 
          {"label": "Contestants", "value": False}
        ],
        value=[True, False],
        multi=True
      )
    ),
    utils.FormElement(
      label="Show(s)",
      element=MultiDropDown(
        id="shows",
        values=["Bachelor", "Bachelorette"]
      )
    ),
    utils.FormElement(
      label="Year(s)",
      element=dcc.RangeSlider(
        id="years",
        min=2002,
        max=2018,
        step=1,
        marks={2002: 2002, 2010: 2010, 2018: 2018},
        value=[2002, 2018]
      ),
      add_elements=[
        html.Br(), 
        html.P(id="selected-years", className="text-right small")
      ]
    ),
    utils.FormElement(
      label="Comparison Specificity",
      element=dcc.Dropdown(
        id="race",
        options=[
          {"label": "POC / Non-POC", "value": "poc_flag"},
          {"label": "All categories", "value": "all"}
        ],
        value="poc_flag"
      )
    )
  ]
)

##### tabs #####

overall_tab = Tab(
  label="Overall", 
  value="overall", 
  children=[
    html.Div(id="overall-value", style=dict(display="none")),
    html.H3("POC are under-represented on the Bachelor/ette"),
    dcc.Graph(id="overall-graph"),
    html.H4(
      "However you cut it, very few people of color make it onto the " \
      + "Bachelor and Bachelorette. Within this data selection:"),
    html.Br(),
    dcc.Markdown(id="overall-caption", className="caption"),
  ]
)

evolution_tab = Tab(
  label="Evolution", 
  value="evolution",
  children=[
    html.H3("POC representation has improved over time"),
    dcc.Graph(id="evolution-graph"),
    html.H4("In recent years, there have been considerably higher numbers " \
      + "of people of color on the Bachelor/ette - including the franchise's " \
      + "first non-white leads.")
  ]
)

comparison_tab = Tab(
  label="Comparison", 
  value="comparison",
  children=[
    html.H3("The Bachelor/ette is still less diverse than the U.S. at large"),
    dcc.Graph(id="comparison-graph"),
    html.H4("Some text")
  ]
)

panel = html.Div(
  className="col-sm-9 text-center",
  children=utils.Tabs(
    value="overall",
    children=[
      overall_tab,
      evolution_tab,
      comparison_tab,
    ]
  )
)

main_content = html.Div(
  className="row",
  children=[dashboard, panel]
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)

########## interactive routes ##########

##### helper functions #####

def get_filtered_df(leads, shows, years):
  start, end = years
  return df[
    (df["race_data_flag"] == True)
    & (df["show"].isin(shows))
    & (df["year"] >= start)
    & (df["year"] <= end)
  ]

def get_race_titles():
  race_flags = ["white", "afam", "amin", "hisp", "asn_paci", "oth", "mult"]
  race_titles = ["White", "African American", "American Indian", "Hispanic",
                 "Asian & Pacific Islander", "Other", "Multiple"]
  return dict(zip(race_flags, race_titles))

def get_poc_name(x):
  return {True: "POC", False: "White"}[x]

def get_lead_name(x):
  return {True: "Leads", "true": "Leads", 
          False: "Contestants", "false": "Contestants"}[x]

def get_layout_font():
  return dict(font=dict(family="Karla"))

##### other routes #####

@app.callback(
  Output(component_id="selected-years", component_property="children"),
  [Input(component_id="years", component_property="value")])
def update_selected_years(years):
  """ shows user what the selected year range is """
  start, end = years
  return "Selected: ({start}, {end})".format(start=start, end=end)

##### overall tab routes #####

@app.callback(
  Output("overall-value", "children"),
  [Input(input_id, "value") for input_id in 
    ["leads", "shows", "years", "race"] ]
)
def clean_overall_data(leads, shows, years, race):
  filtered_df = get_filtered_df(leads, shows, years)
  lead_data = {}
  for lead in leads:
    lead_df = filtered_df[filtered_df["lead_flag"] == lead]
    if race == "poc_flag":
      poc_series = lead_df["poc_flag"].map(get_poc_name)
      counter = Counter(poc_series)
      lead_data[lead] = dict(counter)
    # when we want disaggregated race categories
    elif race == "all":
      race_title_dict = get_race_titles()
      counts = lead_df.count()
      counter = {race_title_dict.get(race_flag): int(counts[race_flag]) 
                 for race_flag in race_title_dict.keys()}
      lead_data[lead] = dict(counter)
  return json.dumps(lead_data)

@app.callback(
  Output("overall-graph", "figure"),
  [Input("overall-value", "children"), Input("race", "value")]
)
def update_overall_graph(cleaned_data, race):
  """ generates figure for overall tab """
  data = json.loads(cleaned_data)
  if not data:
    return dict(data=[], layout=go.Layout())
  groupings = ["White", "POC"] if race == "poc_flag" else \
              list(get_race_titles().values())
  colors = utils.get_colors(groupings)
  traces = []
  for val in groupings:
    x_init = data.keys()
    y = [data.get(x).get(val) for x in x_init]
    x = list(map(get_lead_name, x_init))
    strat_bar = go.Bar(
      x=x,
      y=y,
      hoverinfo="x+y",
      marker=dict(color=colors.get(val)),
      name=val
    )
    traces.append(strat_bar)
  layout = go.Layout(
    xaxis=dict(tickfont=dict(size=14)),
    yaxis=dict(title="Number of People", titlefont=dict(size=16)),
    hovermode="closest",
    **get_layout_font()
  )
  return dict(data=traces, layout=layout)

@app.callback(
  Output("overall-caption", "children"),
  [Input("overall-value", "children"), Input("race", "value")]
)
def update_overall_caption(cleaned_data, race):
  data = json.loads(cleaned_data)
  if not data or race != "poc_flag":
    return "##### Sorry! There are no stats available about this selection"
  caption_elts = []
  for v in data.keys():
    title = {"true": "leads", "false": "contestants"}[v]
    num_poc = data.get(v).get("POC")
    num_npoc = data.get(v).get("White")
    if num_npoc and not num_poc:
      temp = "##### There are no POC {title} for this selection"
      caption_elts.append(temp.format(title=title))
    elif num_poc and not num_npoc:
      temp = "##### There are no white {title} for this selection"
      caption_elts.append(temp.format(title=title))
    elif num_poc and num_npoc:
      temp = "##### There are {mult} times as many white {title} " \
             + "as there are POC {title}"
      mult = round(float(num_npoc)/num_poc, 1)
      caption_elts.append(temp.format(mult=mult, title=title))
  caption = "  \n".join(caption_elts)
  return caption

##### evolution tab routes #####

def get_evol_yearly_data(lead_df, flag_name, flag_value):
  """ 
  returns the % times a flag is equal to a certain value, for all
  years in lead_df
  """
  group_vals = lead_df[flag_name].groupby(lead_df["year"])
  x = []
  y = []
  for year, vals in group_vals:
    counter = Counter(vals)
    total = sum(counter.values())
    # if flag val isn't in counter, it appeared 0 times
    num_flag = counter.get(flag_value, 0)
    perc_flag = round((float(num_flag)/total) * 100, 2)
    y.append(perc_flag)
    x.append(year)
  return x, y

def get_evol_trace(x, y, color, name):
  return go.Scatter(
    x=x,
    y=y,
    hoverinfo="x+y",
    marker=dict(color=color, size=8),
    name=name,
    mode="markers")

@app.callback(
  Output("evolution-graph", "figure"),
  [Input(input_id, "value") for input_id in 
    ["leads", "shows", "years", "race"] ]
)
def update_evolution_graph(leads, shows, years, race):
  filtered_df = get_filtered_df(leads, shows, years)
  layout_all = dict(
    xaxis=dict(title="Year", tickfont=dict(size=14)),
    width=800,
    hovermode="closest",
    **get_layout_font())
  
  if race == "poc_flag":
    traces = []
    colors = utils.get_colors(leads)
    layout = go.Layout(
      yaxis=dict(title="Percentage POC (%)", titlefont=dict(size=16)), 
      height=500,
      **layout_all)
    for lead in leads:
      lead_df = filtered_df[filtered_df["lead_flag"] == lead]
      color = colors.get(lead)
      x, y = get_evol_yearly_data(lead_df, "poc_flag", True)
      trace = get_evol_trace(x=x, y=y, color=color, name=get_lead_name(lead))
      traces.append(trace)
    return dict(data=traces, layout=layout)

  elif race == "all":
    fig = tools.make_subplots(
      rows=len(leads), cols=1, 
      subplot_titles=tuple([get_lead_name(lead) for lead in leads]) )

    race_title_dict = get_race_titles()
    race_title_dict.pop("white")
    colors = utils.get_colors(race_title_dict.keys())
    
    # new subplot per lead
    for row, lead in enumerate(leads):
      lead_df = filtered_df[filtered_df["lead_flag"] == lead]
      total = lead_df.count()
      for flag, title in race_title_dict.items():
        x, y = get_evol_yearly_data(lead_df, flag, 1)
        trace = get_evol_trace(x=x, y=y, color=colors.get(flag), name=title)
        fig.append_trace(trace, row + 1, 1)

    fig["layout"].update(height=350*len(leads), **layout_all)
    return fig
  return dict(data=[], layout=go.Layout())

##### comparison tab routes #####

@app.callback(
  Output("comparison-graph", "figure"),
  [Input(input_id, "value") for input_id in 
    ["leads", "shows", "years", "race"] ]
)
def update_comparison_graph(leads, shows, years, race):
  filtered_df = get_filtered_df(leads, shows, years)
  traces = []
  colors = utils.get_colors(leads)


  layout = go.Layout()
  return dict(data=traces, layout=layout)
