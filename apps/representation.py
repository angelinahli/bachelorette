import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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

########## designing general ui ##########

# what goes on this page:
# 1. proportion of people that are white / non white overall
# 2. proportion of leads that are white / non white overall
# 3. clickable 

# define main content
class BSDashboard(html.Div):
  def __init__(self, children):
    super().__init__(className="col-sm-3")
    self.children = [html.Br()] + children

class BSPanel(html.Div):
  def __init__(self, children, heading=None):
    super().__init__(className="col-sm-9 text-center")
    self.children = [html.Br()] + children

class BSTabContent(html.Div):
  def __init__(self, dashboard, panel, **kwargs):
    super().__init__(className="row", **kwargs)
    self.children = [dashboard, panel]

class MultiDropDown(dcc.Dropdown):
  def __init__(self, values, **kwargs):
    super().__init__(
      options=utils.get_form_options(values),
      value=list(map(lambda x: x.lower(), values)),
      multi=True,
      **kwargs)

# the number of POC vs. non-POC
overall_tab = dcc.Tab(
  label="Overall", 
  value="overall", 
  children=BSTabContent(
    dashboard=BSDashboard([
      html.H4("Change the specificity of this chart below"),
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
      )
    ]),
    panel=BSPanel([
      dcc.Graph(id="overall-bar")
    ])
  )
)

evolution_tab = dcc.Tab(
  label="Evolution", 
  value="evolution")

comparison_tab = dcc.Tab(
  label="Comparison", 
  value="comparison")

interactive_tab = dcc.Tab(
  label="Interactive", 
  value="interactive")

main_content = utils.Tabs(
  id="tabs",
  value="overall",
  children=[
    overall_tab,
    evolution_tab,
    comparison_tab,
    interactive_tab
  ]
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)

########## interactive routes ##########

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)

@app.callback(
  Output(component_id="overall-bar", component_property="figure"),
  [Input(component_id="leads", component_property="value")]
)
def update_overall_tab(leads):
  """ generates figure for overall tab """
  filtered_df = df[df["race_data_flag"] == True][
    ["lead_flag", "race_data_flag", "poc_flag"]
  ]
  traces = []
  for poc_val in [True, False]:
    poc_series = filtered_df[df["poc_flag"] == poc_val]["lead_flag"]
    poc_series = poc_series[poc_series.isin(leads)] \
                 .map(lambda x: {True: "Leads", False: "Candidates"}[x])
    groupings = Counter(poc_series)
    strat_bar = go.Bar(
      x=list(groupings.keys()),
      y=list(groupings.values()),
      hoverinfo="x+y",
      name="POC" if poc_val else "Non-POC"
    )
    traces.append(strat_bar)
  layout = go.Layout()
  return dict(data=traces, layout=layout)

