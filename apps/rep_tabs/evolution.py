import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from numpy import polyfit
from plotly import tools
from plotly.graph_objs import Layout


import utils
from app import app
from apps import rep

stub = "evol-rep-"

tab = dcc.Tab(label="Evolution", value="evolution")

content = utils.TabContent(
  dashboard=utils.Dashboard([
    utils.ShowsElement(elt_id=stub + "shows"),
    utils.YearsElement(elt_id=stub + "years"),
    utils.RaceElement(elt_id=stub + "race")
  ]),
  panel=utils.Panel([
    html.H4("POC representation has improved over time"),
    dcc.Graph(id=stub + "graph"),
    html.H5([
      """
      In recent years, a higher number of people of color have
      participated in the Bachelor/ette.
      """,
      html.Br(), html.Br(),
      """
      Representation of POC contestants rose sharply after two rejected
      applicants filed a racial discrimination lawsuit against the
      franchise in 2012.
      """])
  ])
)

def get_reg(x, y, beta_1, beta_0, color, name, **kwargs):
  return utils.Scatter(
    x=x,
    y=list(map(lambda x_val: beta_0 + (beta_1 * x_val), x)),
    color=color,
    name=name,
    mode="lines+text",
    **kwargs)

def get_poc_fig(df, layout_all):
  layout = Layout(
    yaxis=dict(title="% Candidates"), 
    annotations=[],
    height=500,
    **layout_all
  )
  traces = []
  x, y = utils.get_yearly_data(df, "poc", 1)
  b1, b0 = polyfit(x, y, 1)
  color = utils.get_race_color("poc")
  traces.append(utils.Scatter(x=x, y=y, color=color, name="Values"))
  traces.append(get_reg(x, y, b1, b0, color, "OLS Estimates"))
  rep.add_2012_lawsuit_annot(x, y, layout)
  return dict(data=traces, layout=layout)

def get_all_fig(df, end_year, layout_all):
  race_titles = dict(utils.RACE_TITLES)
  race_titles.pop("white")
  race_keys = utils.get_ordered_race_flags(race_titles.keys())

  rows, cols = 3, 2
  order = [(r, c) for r in range(1, rows + 1) for c in range(1, cols + 1)]
  trace_pos = dict(zip(race_keys, order))

  fig = tools.make_subplots(
    rows=rows, cols=cols, 
    vertical_spacing = 0.1,
    subplot_titles=tuple(race_titles.get(k) for k in race_keys) )

  # new subplot per racial category
  axis_num = 1
  all_y = []
  b1_vals = {}
  for flag in race_keys:
    xaxis = "xaxis{}".format(axis_num)
    yaxis = "yaxis{}".format(axis_num)
    color = utils.get_race_color(flag)
    row, col = trace_pos.get(flag)
    title = race_titles.get(flag)

    x, y = utils.get_yearly_data(df, flag, 1)
    b1, b0 = polyfit(x, y, 1)
    scatter = utils.Scatter(x=x, y=y, color=color, name=title, 
                            xaxis=xaxis, yaxis=yaxis, size=6)
    reg = get_reg(x, y, b1, b0, color, title)
    all_y += y
    b1_vals[axis_num] = b1

    fig.append_trace(scatter, row, col)
    fig.append_trace(reg, row, col)

    fig["layout"].update( 
      {yaxis: dict(title="% Candidates")})
    axis_num += 1

  min_y = min(0, min(all_y))
  max_y = max(all_y)
  inc = (max_y - min_y)/11.0
  for num in range(1, axis_num):
    fig["layout"]["yaxis{}".format(num)].update(range=[min_y - inc, max_y + inc])
    fig["layout"]["annotations"].append(
      dict(
        x=end_year - round(inc), y=max_y - inc,
        align="left",
        xref="x{}".format(num), yref="y{}".format(num),
        text=u"β1 = {}".format(round(b1_vals.get(num), 2)),
        **utils.LAYOUT_ANN) )

  fig["layout"].update(height=300*rows, showlegend=False, **layout_all)
  return fig

@app.callback(
  Output(stub + "graph", "figure"),
  [Input(input_id, "value") for input_id in 
    [stub + "shows", stub + "years", stub + "race"] ]
)
def update_graph(shows, years, race):
  df = rep.get_filtered_df([False], shows, years)
  start = df.year.min()
  end = df.year.max()
  layout_all = dict(
    title="Percentage of Contestants that are POC<br>{}-{}".format(start, end),
    **utils.LAYOUT_ALL)

  if race == "poc_flag":
    return get_poc_fig(df, layout_all)
  elif race == "all":
    return get_all_fig(df, end, layout_all)
  return dict(data=[], layout=Layout())

@app.callback(
  Output("selected-" + stub + "years", "children"),
  [Input(stub + "years", "value")])
def update_years(years):
  return utils.update_selected_years(years)