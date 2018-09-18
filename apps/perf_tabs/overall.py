import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import numpy as np
from collections import Counter
from plotly.graph_objs import Layout

import utils
from app import app
from apps import perf

stub = "over-perf-"

tab = dcc.Tab(label="Overall", value="overall")

content = utils.TabContent(
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.Div(id=stub + "value", style=dict(display="none")),
    html.H4(
      """
      POC candidates stay on the show for about as long as non-POC candidates
      """),
    dcc.Graph(id=stub + "graph"),
    html.Br(),
    html.H5([
      """
      While overall, POC candidates exit from the Bachelor/ette earlier in
      a shows' run than their non-POC counterparts, this difference is
      minimal in magnitude.
      """, 
      html.Br(), html.Br(),
      """
      In fact, some populations of non-white candidates appear to stay on the
      show for longer than their white peers.
      """]),
    html.H6(id=stub + "caption", className="caption")
  ])
)

@app.callback(
  Output(stub + "graph", "figure"),
  [Input(stub + inp, "value") for inp in ["shows", "years", "race"] ]
)
def update_graph(shows, years, race):
  if not race:
    return dict(data=[], layout=Layout())

  traces = []
  df = perf.get_filtered_df(shows, years)
  title_dict = utils.POC_TITLES if race == "poc_flag" else utils.RACE_TITLES
  x_vals = utils.get_ordered_race_flags(title_dict.keys())
  for flag in x_vals:
    series = df[df[flag] == 1].perc_weeks.map(lambda x: x * 100)
    title = title_dict.get(flag)
    trace = dict(
      type="violin",
      x=title,
      y=series,
      name=title,
      box=dict(visible=True),
      meanline=dict(visible=True),
      showlegend=False,
      line=dict(color=utils.get_race_color(flag)))
    traces.append(trace)
  
  show_names = " & ".join(shows)
  start = df.year.min()
  end = df.year.max()
  layout = Layout(
    title="Percentage of Season {} Candidates Last<br>{}-{}".format(
      show_names, start, end),
    xaxis=dict(tickfont=dict(size=14)),
    yaxis=dict(title="% Season"), 
    margin=dict(b=120 if race == "all" else 50),
    **utils.LAYOUT_ALL)
  return dict(data=traces, layout=layout)

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)