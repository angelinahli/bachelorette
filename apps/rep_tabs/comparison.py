import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import plotly.graph_objs as go

import utils
from app import app
from apps import rep

stub = "comp-"

tab = dcc.Tab(label="Comparison", value="comparison")

content = utils.TabContent(
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.Div(id=stub + "value", style=dict(display="none")),
    html.H4("The Bachelor/ette is still less diverse than the U.S."),
    dcc.Graph(id=stub + "graph"),
    html.H5([
      "While the Bachelor/ette has started to cast a more diverse cast, ",
      "the franchise is still much less diverse than Americans as a population."
    ]),
    html.H6(id=stub + "caption", className="caption")
  ])
)

def get_values(census_df, cands, flag, title):
  # helper function for clean_data
  cens = dict(zip(census_df.year, census_df[flag + "_perc"].map(lambda x: x*100)))
  years = list(filter(lambda yr: yr in cands.keys(), cens))
  color = utils.get_race_color(flag)
  return dict(cands=cands, cens=cens, years=years, color=color, title=title)

def get_percs(values):
  return [
    round(
        values.get("cands").get(str(yr)) 
        - values.get("cens").get(str(yr)), 
      1) 
    for yr in values.get("years")]

@app.callback(
  Output(stub + "value", "children"),
  [Input(stub + input_stub, "value") for input_stub in 
    ["shows", "years", "race"] ]
)
def clean_data(shows, years, race):
  df = rep.get_filtered_df([False], shows, years)
  census_df = rep.census
  values = {}
  
  if race == "all":
    titles = dict(utils.RACE_TITLES)
    titles.pop("oth")
    for flag, title in titles.items():
      cands = rep.get_yearly_data(df, flag, 1, get_dict=True)
      values[flag] = get_values(census_df, cands, flag, title)
  
  elif race == "poc_flag":
    cands = rep.get_yearly_data(df, "poc_flag", True, get_dict=True)
    title = rep.get_poc_name(True)
    values["nwhite"] = get_values(census_df, cands, "nwhite", title)

  return json.dumps(values)

@app.callback(
  Output(stub + "graph", "figure"), 
  [
    Input(stub + "value", "children"), 
    Input(stub + "years", "value"),
    Input(stub + "race", "value")
  ])
def update_graph(cleaned_data, years, race):
  data = json.loads(cleaned_data)
  traces = []
  start, end = years
  layout = go.Layout(
    title="Difference in Percentage POC of U.S. Population and<br>" \
      + "Percentage POC of Bachelor/ette Contestants<br>" \
      + "{}-{}".format(start, end),
    yaxis=dict(title="Percentage Point<br>Difference"),
    height=500,
    **utils.LAYOUT_ALL)

  if race == "poc_flag":
    values = data["nwhite"]
    percs = get_percs(values)
    trace = utils.Bar(
      x=values.get("years"), 
      y=percs, 
      text=percs,
      colors=values.get("color"), 
      name=values.get("title")
    )
    traces.append(trace)

  elif race == "all":
    for flag, values in data.items():
      trace = go.Scatter(
        x=values.get("years"),
        y=get_percs(values),
        hoverinfo="x+y",
        marker=dict(color=values.get("color")),
        name=values.get("title"))
      traces.append(trace)

  return dict(data=traces, layout=layout)

@app.callback(
  Output(stub + "caption", "children"), 
  [Input(stub + "race", "value"), Input(stub + "value", "children")])
def update_caption(race, cleaned_data):
  flag_values = json.loads(cleaned_data)

  get_perc = lambda vals, val_type, yr: round(vals.get(val_type).get(yr), 1)
  if race == "poc_flag":
    poc_vals = flag_values.get("nwhite")
    last_yr = str(max(map(int, poc_vals.get("years"))))
    return ("In {yr}, {perc_cands}% of candidates were POC. By contrast, " \
      + "in that year {perc_cens}% of Americans were POC.").format(
        yr=last_yr, 
        perc_cands=get_perc(poc_vals, "cands", str(last_yr)),
        perc_cens=get_perc(poc_vals, "cens", str(last_yr))
      )

  elif race == "all":
    afam = flag_values.get("afam")
    hisp = flag_values.get("hisp")
    # last year where both have data
    last_yr = str(min(
      max(map(int, afam.get("years"))), 
      max(map(int, hisp.get("years")))
    ))
    return ("African Americans and Hispanics are particularly " \
      + "underrepresented on the franchise. In {yr}, {pcand_afam}% " \
      + "of candidates were African American and {pcand_hisp}% were " \
      + "Hispanic. By contrast, in that year {pcens_afam}% of the " \
      + "American population was African American, and {pcens_hisp}% " \
      + "was Hispanic.").format(
        yr=last_yr,
        pcand_afam=get_perc(afam, "cands", last_yr),
        pcand_hisp=get_perc(hisp, "cands", last_yr),
        pcens_afam=get_perc(afam, "cens", last_yr),
        pcens_hisp=get_perc(hisp, "cens", last_yr))

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)