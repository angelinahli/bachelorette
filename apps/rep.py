import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import os
import pandas as pd
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
    html.Br(),
    html.H5("Change what this figure shows below:"),
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
      element=MultiDropDown(
        id="years",
        values=range(2002, 2019)
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
    html.H2("People of Color on the Bachelor/ette"),
    dcc.Graph(id="overall-bar"),
    dcc.Markdown(id="overall-caption")
  ]
)

evolution_tab = Tab(
  label="Evolution", 
  value="evolution",
  children=[]
)

comparison_tab = Tab(
  label="Comparison", 
  value="comparison",
  children=[]
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

@app.callback(
  Output("overall-value", "children"),
  [Input(input_id, "value") for input_id in 
    ["leads", "shows", "years"] ]
)
def clean_overall_data(leads, shows, years):
  filtered_df = df[
    (df["race_data_flag"] == True)
    & (df["show"].isin(shows))
    * (df["year"].isin(years)) ][
    ["lead_flag", "race_data_flag", "poc_flag"]
  ]
  groupings = {}
  poc_vals = [True, False]
  for poc_val in poc_vals:
    poc_series = filtered_df[df["poc_flag"] == poc_val]["lead_flag"]
    poc_series = poc_series[poc_series.isin(leads)] \
                 .map(lambda x: {True: "Leads", False: "Contestants"}[x])
    counter = Counter(poc_series)
    group_vars = {"x": list(counter.keys()), "y": list(counter.values())}
    groupings[poc_val] = group_vars
  return json.dumps(groupings)

@app.callback(
  Output("overall-bar", "figure"),
  [Input("overall-value", "children")]
)
def update_overall_tab(cleaned_data):
  """ generates figure for overall tab """
  groupings = json.loads(cleaned_data)
  poc_vals = ["true", "false"]
  colors = dict(zip(poc_vals, utils.COLORSCHEME))
  traces = []
  for poc_val, group_vars in groupings.items():
    strat_bar = go.Bar(
      x=group_vars.get("x"),
      y=group_vars.get("y"),
      hoverinfo="x+y",
      marker=dict(color=colors.get(poc_val, utils.PRIMARY_COLOR)),
      name="POC" if poc_val == "true" else "White"
    )
    traces.append(strat_bar)
  layout = go.Layout(
    xaxis=dict(tickfont=dict(size=14)),
    yaxis=dict(title="Number of People", titlefont=dict(size=16)),
    hovermode="closest"
  )
  return dict(data=traces, layout=layout)

@app.callback(
  Output("overall-caption", "children"),
  [Input("leads", "value"), Input("overall-value", "children")]
)
def update_overall_caption(leads, cleaned_data):
  groupings = json.loads(cleaned_data)
  leads = map(lambda x: {True: "Leads", False: "Contestants"}[x], leads)

  new_groupings = {}
  for k, v in groupings.items():
    key = "num_poc" if k == "true" else "num_npoc"
    val = dict(zip(v.get("x"), v.get("y")))
    new_groupings[key] = val

  template = "##### There are {mult} times as many white {title} " \
             + "as there are POC {title}"
  caption_elts = []
  for v in leads:
    num_poc = new_groupings.get("num_poc").get(v)
    num_npoc = new_groupings.get("num_npoc").get(v)
    title = v.lower()
    if num_npoc and not num_poc:
      temp = "##### There are no POC {title} for this selection"
      caption_elts.append(temp.format(title=title))
    elif num_poc and not num_npoc:
      temp = "##### There are no white {title} for this selection"
      caption_elts.append(temp.format(title=title))
    elif num_poc and num_npoc:
      mult = round(float(num_npoc)/num_poc, 1)
      caption_elts.append(template.format(mult=mult, title=v.lower()))

  caption = "  \n".join(caption_elts)
  return caption
