import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import os
import pandas as pd
import plotly.graph_objs as go

from collections import Counter
from numpy import polyfit
from plotly import tools

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

########## designing general ui ##########

##### dashboard elements #####

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
      element=MultiDropDown(
        id=elt_id,
        values=["Bachelor", "Bachelorette"]
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

##### tabs #####

overall_tab = Tab(
  label="Overall", 
  value="overall", 
  dashboard=Dashboard([
    LeadsElement(elt_id="overall-leads"),
    ShowsElement(elt_id="overall-shows"),
    YearsElement(elt_id="overall-years"),
    RaceElement(elt_id="overall-race")
  ]),
  panel=Panel([
    html.Div(id="overall-value", style=dict(display="none")),
    html.H3("POC are under-represented on the Bachelor/ette"),
    dcc.Graph(id="overall-graph"),
    html.H4(
      "However you cut it, very few people of color make it onto the " \
      + "Bachelor and Bachelorette. Within this data selection:"),
    html.Br(),
    dcc.Markdown(id="overall-caption", className="caption"),
  ])
)

evolution_tab = Tab(
  label="Evolution", 
  value="evolution",
  dashboard=Dashboard([
    ShowsElement(elt_id="evol-shows"),
    YearsElement(elt_id="evol-years"),
    RaceElement(elt_id="evol-race")
  ]),
  panel=Panel([
    html.H3("POC representation has improved over time"),
    dcc.Graph(id="evol-graph"),
    html.H4("In recent years, there have been considerably higher numbers " \
      + "of people of color on the Bachelor/ette - including the franchise's " \
      + "first non-white leads."),
    html.H5(id="evol-caption", className="caption")
  ])
)

comparison_tab = Tab(
  label="Comparison", 
  value="comparison",
  dashboard=Dashboard([
    LeadsElement(elt_id="comp-leads"),
    ShowsElement(elt_id="comp-shows"),
    YearsElement(elt_id="comp-years"),
    RaceElement(elt_id="comp-race")
  ]),
  panel=Panel([
    html.H3("The Bachelor/ette is still less diverse than the U.S. at large"),
    dcc.Graph(id="comparison-graph"),
    html.H4("Some text")
  ])
)

main_content = html.Div(
  className="row",
  children=utils.Tabs(
  value="overall",
  children=[overall_tab, evolution_tab, comparison_tab])
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
  race_titles = ["White", "African American", "Native American", "Hispanic",
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

def update_selected_years(years):
  """ shows user what the selected year range is """
  start, end = years
  return "Selected: ({start}, {end})".format(start=start, end=end)

@app.callback(
  Output("selected-overall-years", "children"),
  [Input("overall-years", "value")])
def update_overall_years(years):
  return update_selected_years(years)

@app.callback(
  Output("selected-evol-years", "children"),
  [Input("evol-years", "value")])
def update_evol_years(years):
  return update_selected_years(years)

@app.callback(
  Output("selected-comp-years", "children"),
  [Input("comp-years", "value")])
def update_comp_years(years):
  return update_selected_years(years)

##### overall tab routes #####

@app.callback(
  Output("overall-value", "children"),
  [Input(input_id, "value") for input_id in 
    ["overall-leads", "overall-shows", "overall-years", "overall-race"] ]
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
  [Input("overall-value", "children"), Input("overall-race", "value")]
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
  [Input("overall-value", "children"), Input("overall-race", "value")]
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

def get_evol_yearly_data(df, flag_name, flag_value):
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
  return x, y

def get_evol_scatter(x, y, color, name, **kwargs):
  return go.Scatter(
    x=x, y=y,
    hoverinfo="x+y",
    marker=dict(color=color, size=8),
    name=name,
    mode="markers",
    **kwargs)

def get_evol_reg(x, y, color, name, **kwargs):
  beta_1, beta_0 = polyfit(x, y, 1)
  return go.Scatter(
    x=x,
    y=list(map(lambda x_val: beta_0 + (beta_1 * x_val), x)),
    hoverinfo="x+y",
    marker=dict(color=color, size=2),
    name=name,
    mode="lines",
    **kwargs)

def get_race_poc_fig(df, layout_all):
  traces = []
  layout = go.Layout(
    xaxis=dict(title="Year", tickfont=dict(size=14)),
    yaxis=dict(title="Percentage POC (%)", titlefont=dict(size=16)), 
    height=550,
    **layout_all)
  x, y = get_evol_yearly_data(df, "poc_flag", True)
  traces.append(get_evol_scatter(x, y, utils.PRIMARY_COLOR, "Values"))
  traces.append(get_evol_reg(x, y, utils.PRIMARY_COLOR, "OLS Estimates"))
  return dict(data=traces, layout=layout)

def get_race_all_fig(df, layout_all):
  race_title_dict = get_race_titles()
  race_title_dict.pop("white")
  colors = utils.get_colors(race_title_dict.keys())

  rows, cols = 3, 2
  order = [(r, c) for r in range(1, rows + 1) for c in range(1, cols + 1)]
  trace_pos = dict(zip(race_title_dict.keys(), order))

  fig = tools.make_subplots(
    rows=rows, cols=cols, 
    subplot_titles=tuple(race_title_dict.values()) )

  # new subplot per racial category
  i = 1
  for flag, title in race_title_dict.items():
    color = colors.get(flag)
    row, col = trace_pos.get(flag)
    x, y = get_evol_yearly_data(df, flag, 1)
    xaxis = "xaxis{}".format(i)
    yaxis = "yaxis{}".format(i)
    scatter = get_evol_scatter(x, y, color, title, xaxis=xaxis, yaxis=yaxis)
    reg = get_evol_reg(x, y, color, title)
    fig.append_trace(scatter, row, col)
    fig.append_trace(reg, row, col)
    fig["layout"].update( 
      {xaxis: dict(title="Year"), yaxis: dict(title="Percentage (%)")} )
    i += 1

  fig["layout"].update(height=350*rows, showlegend=False, **layout_all)
  return fig

@app.callback(
  Output("evol-graph", "figure"),
  [Input(input_id, "value") for input_id in 
    ["evol-shows", "evol-years", "evol-race"] ]
)
def update_evol_graph(shows, years, race):
  df = get_filtered_df(leads=[False], shows=shows, years=years)
  start, end = years
  layout_all = dict(
    title="Percentage POC Contestants (%), {}-{}".format(start, end),
    hovermode="closest",
    **get_layout_font())

  if race == "poc_flag":
    return get_race_poc_fig(df, layout_all)
  elif race == "all":
    return get_race_all_fig(df, layout_all)
  return dict(data=[], layout=go.Layout())

@app.callback(Output("evol-caption", "children"), [Input("evol-race", "value")])
def update_evol_caption(race):
  captions = {
    "poc_flag": "",
    "all": "Some racial groups have seen much larger increases in " \
           + "representation than others."
  }
  return

# ##### comparison tab routes #####

# @app.callback(
#   Output("comparison-graph", "figure"),
#   [Input("comp-" + input_stub, "value") for input_stub in 
#     ["leads", "shows", "years", "race"] ]
# )
# def update_comparison_graph(leads, shows, years, race):
#   filtered_df = get_filtered_df(leads, shows, years)
#   traces = []
#   colors = utils.get_colors(leads)


#   layout = go.Layout()
#   return dict(data=traces, layout=layout)
