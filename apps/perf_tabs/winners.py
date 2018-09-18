import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
from plotly.graph_objs import Layout, Bar

import utils
from app import app
from apps import perf

stub = "winner-"

tab = dcc.Tab(label="Winners", value="winners")

content = utils.TabContent(
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.Div(id=stub + "value", style=dict(display="none")),
    html.H4(
      "Very few people of color win the Bachelor/ette"),
    dcc.Graph(id=stub + "graph"),
    html.H5([
      """
      Although the average POC candidate on the Bachelorette stays on the show 
      for about as long as the average white candidate, when push comes to shove
      the shows' leads almost always choose non-POC winners.
      """,
      html.Br(), html.Br(),
      """
      All of the shows' three nonwhite Bachelor/ettes ended up selecting 
      white winners.
      """
    ])
  ])
)

@app.callback(
  Output(stub + "graph", "figure"),
  [Input(stub + inp, "value") for inp in ["shows", "years", "race"] ]
)
def update_graph(shows, years, race):
  """ generates figure for overall tab """
  if not race:
    return dict(data=[], layout=Layout())

  df = perf.get_filtered_df(shows, years)
  
  title_dict = utils.POC_TITLES if race == "poc_flag" else utils.RACE_TITLES
  x_vals = utils.get_ordered_race_flags(title_dict.keys())
  x = list(map(title_dict.get, x_vals))
  colors = []
  y = []
  for flag in x_vals:
    series = df[(df[flag] == 1) & (df["winner_flag"] == True)]
    colors.append(utils.get_race_color(flag))
    y.append(series.shape[0]) # first val: row count

  bar = Bar(
    x=x, y=y,
    hoverinfo="x+y",
    marker=dict(color=colors),
    text=y,
    textposition="auto")

  show_names = " & ".join(shows)
  start = df.year.min()
  end = df.year.max()
  layout = Layout(
    title="Winners on the {}<br>{}-{}".format(show_names, start, end),
    xaxis=dict(tickfont=dict(size=14)),
    yaxis=dict(title="# People"),
    margin=dict(b=120 if race == "all" else 50),
    **utils.LAYOUT_ALL
  )
  return dict(data=[bar], layout=layout)

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)