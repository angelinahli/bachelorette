import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import plotly.graph_objs as go
from collections import Counter

import utils
from app import app
from apps import rep

stub = "over-rep-"

tab = dcc.Tab(label="Overall", value="overall")

content = utils.TabContent(
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    rep.LeadElement(elt_id=stub + "lead"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.Div(id=stub + "value", style=dict(display="none")),
    html.H4("POC are under-represented on the Bachelor/ette"),
    dcc.Graph(id=stub + "graph"),
    html.H5(
      """
      However you cut it, very few people of color make it onto the
      Bachelor and Bachelorette. Within this data selection:
      """),
    html.H6(id=stub + "caption", className="caption")
  ])
)

def get_lead_name(x):
  return {True: "Bachelor/ettes", "true": "Bachelor/ettes", 
          False: "Contestants", "false": "Contestants"}[x]

@app.callback(
  Output(stub + "value", "children"),
  [Input(stub + input_stub, "value") for input_stub in 
    ["lead", "shows", "years", "race"] ]
)
def clean_data(lead, shows, years, race):
  filtered_df = rep.get_filtered_df(lead, shows, years)
  data = dict(x=None, y=[], colors=[])

  if not race:
    return json.dumps(data)

  title_dict = utils.POC_TITLES if race == "poc_flag" else utils.RACE_TITLES
  x_vals = utils.get_ordered_race_flags(title_dict.keys())
  data["x"] = list(map(title_dict.get, x_vals))
  for flag in x_vals:
    series = filtered_df[filtered_df[flag] == 1]
    data["colors"].append(utils.get_race_color(flag))
    data["y"].append(series.shape[0]) # first val: row count
  return json.dumps(data)

@app.callback(
  Output(stub + "graph", "figure"),
  [
    Input(stub + "value", "children"),
    Input(stub + "race", "value"), 
    Input(stub + "years", "value"),
    Input(stub + "lead", "value")
  ]
)
def update_graph(cleaned_data, race, years, lead):
  """ generates figure for overall tab """
  data = json.loads(cleaned_data)
  if not data:
    return dict(data=[], layout=go.Layout())

  start, end = years
  title = get_lead_name(lead)
  layout = go.Layout(
    title="Number of {} on the Bachelor/ette<br>{}-{}".format(title, start, end),
    xaxis=dict(tickfont=dict(size=14)),
    yaxis=dict(title="# People"),
    margin=dict(b=120 if race == "all" else 50),
    **utils.LAYOUT_ALL
  )

  bar = utils.Bar(text=data["y"], textposition="auto", **data)
  return dict(data=[bar], layout=layout)

@app.callback(
  Output(stub + "caption", "children"),
  [
    Input(stub + "value", "children"), 
    Input(stub + "race", "value"),
    Input(stub + "lead", "value")
  ]
)
def update_caption(cleaned_data, race, lead):
  data = json.loads(cleaned_data)
  if not data:
    return "Sorry! There are no stats available about this selection"
  
  title = get_lead_name(lead).lower()
  vals = dict(zip(data["x"], data["y"]))

  if race == "all":
    vals.pop("White")
    if not vals:
      return "There are no POC {} for this selection".format(title)
    most_poc = sorted(vals.items(), key=lambda tup: tup[1], reverse=True)[0][0]
    return "Amongst POC {t}, the most represented racial group is: {g}".format(
      t=title,
      g=most_poc)

  num_poc = vals.get("POC")
  num_npoc = vals.get("White")

  if num_npoc and not num_poc:
    return "There are no POC {} for this selection".format(title)
  elif num_poc and not num_npoc:
    return "There are no white {} for this selection".format(title)
  elif num_poc and num_npoc:
    return "There are {x} times as many white {t} as there are POC {t}".format(
      t=title,
      x=round(float(num_npoc)/num_poc, 1)
    )

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)