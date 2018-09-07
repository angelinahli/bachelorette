import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import plotly.graph_objs as go
from collections import Counter

import utils
from app import app
from apps import rep

tab = rep.Tab(
  label="Overall", 
  value="overall", 
  dashboard=rep.Dashboard([
    rep.LeadsElement(elt_id="overall-leads"),
    rep.ShowsElement(elt_id="overall-shows"),
    rep.YearsElement(elt_id="overall-years"),
    rep.RaceElement(elt_id="overall-race")
  ]),
  panel=rep.Panel([
    html.Div(id="overall-value", style=dict(display="none")),
    html.H4("POC are under-represented on the Bachelor/ette"),
    dcc.Graph(id="overall-graph"),
    html.H5(
      "However you cut it, very few people of color make it onto the " \
      + "Bachelor and Bachelorette. Within this data selection:"),
    dcc.Markdown(id="overall-caption", className="caption")
  ])
)

@app.callback(
  Output("overall-value", "children"),
  [Input("overall-" + input_stub, "value") for input_stub in 
    ["leads", "shows", "years", "race"] ]
)
def clean_data(leads, shows, years, race):
  filtered_df = rep.get_filtered_df(leads, shows, years)
  lead_data = {}
  for lead in leads:
    lead_df = filtered_df[filtered_df["lead_flag"] == lead]
    if race == "poc_flag":
      poc_series = lead_df["poc_flag"].map(rep.get_poc_name)
      counter = Counter(poc_series)
      lead_data[lead] = dict(counter)
    # when we want disaggregated race categories
    elif race == "all":
      counts = lead_df.count()
      counter = {flag: int(counts[flag]) for flag in utils.RACE_TITLES.keys()}
      lead_data[lead] = counter
  return json.dumps(lead_data)

@app.callback(
  Output("overall-graph", "figure"),
  [Input("overall-value", "children"), Input("overall-race", "value"), 
    Input("overall-years", "value")]
)
def update_graph(cleaned_data, race, years):
  """ generates figure for overall tab """
  data = json.loads(cleaned_data)
  if not data:
    return dict(data=[], layout=go.Layout())
  start, end = years
  layout = go.Layout(
    title="Number of People on the Bachelor/ette<br>{}-{}".format(start, end),
    xaxis=dict(tickfont=dict(size=14)),
    legend=dict(orientation="h"),
    hovermode="closest",
    margin=dict(b=10),
    **utils.LAYOUT_FONT
  )

  groupings = ["White", "POC"] if race == "poc_flag" else \
              utils.get_ordered_race_flags(utils.RACE_TITLES.keys())
  traces = []
  for val in groupings:
    x_init = data.keys() # leads
    y = [data.get(x).get(val) for x in x_init]
    x = list(map(rep.get_lead_name, x_init))
    color = utils.get_race_color(val)
    title = val if race == "poc_flag" else utils.RACE_TITLES.get(val)
    strat_bar = go.Bar(
      x=x,
      y=y,
      text=y,
      textposition="outside",
      hoverinfo="x+y",
      marker=dict(color=color),
      name=title
    )
    traces.append(strat_bar)
  return dict(data=traces, layout=layout)

@app.callback(
  Output("overall-caption", "children"),
  [Input("overall-value", "children"), Input("overall-race", "value")]
)
def update_caption(cleaned_data, race):
  data = json.loads(cleaned_data)
  if not data or race != "poc_flag":
    return "##### Sorry! There are no stats available about this selection"
  caps = []
  for v in data.keys():
    title = rep.get_lead_name(v).lower()
    num_poc = data.get(v).get("POC")
    num_npoc = data.get(v).get("White")

    if num_npoc and not num_poc:
      caps.append("###### There are no POC {} for this selection".format(title))
    elif num_poc and not num_npoc:
      caps.append("###### There are no white {} for this selection".format(title))
    elif num_poc and num_npoc:
      cap = "###### There are {x} times as many white {t} as there are POC {t}"
      caps.append(cap.format(t=title, x=round(float(num_npoc)/num_poc, 1) ))
  caption = "  \n".join(caps)
  return caption

@app.callback(
  Output("selected-overall-years", "children"),
  [Input("overall-years", "value")])
def update_years(years):
  return rep.update_selected_years(years)