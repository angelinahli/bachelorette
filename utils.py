import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

###### app wide variables ######

PRIMARY_COLOR = "#C95B83"
SECONDARY_COLOR = "#808080"
COLORSCHEME = ["#C95B83", "#FFBD4A", "#F26B3C", "#399E5A", "#5AB1BB", "#1446A0", 
               "#731963"]

RACE_TITLES = {
  "white": "White",
  "afam": "African American",
  "amin": "Native American",
  "hisp": "Hispanic",
  "asn_paci": "Asian & Pacific Islander",
  "oth": "Other",
  "mult": "Multiple"
}

LAYOUT_ALL = dict(
  font=dict(family="Karla"),
  legend=dict(orientation="h"),
  hovermode="closest")
LAYOUT_ANN = dict(
    showarrow=False, 
    font=dict(color=SECONDARY_COLOR, size=14, family="Karla"))

###### app wide classes ######

class BSContainer(html.Div):
  def __init__(self, main_content=None, title=None, subtitle=None, **kwargs):

    super().__init__(className="container", **kwargs)
    self.children = []

    # adding in title
    if title:
      self.children.append( html.H2(className="mt-5", children=title) )

    # adding sub title text
    if subtitle:
      self.children.append( html.P(className="lead text-muted", children=subtitle) )

    # adding body content
    if main_content:
      self.children.append(html.Br())
      self.children.append(main_content)

class Tabs(dcc.Tabs):
  def __init__(self, c_border="#d6d6d6", c_primary=PRIMARY_COLOR, 
               c_back="#f9f9f9", **kwargs):
    super().__init__(
      colors={"border": c_border, "primary": c_primary, "background": c_back},
      **kwargs)

class TabContent(html.Div):
  def __init__(self, dashboard, panel, **kwargs):
    super().__init__(
      className="row",
      children=[dashboard, panel],
      **kwargs)

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
      html.Br(),
    ]
    self.children += form_elements

class FormElement(html.Div):
  """ 
  Dash doesn't package form elements with labels nicely yet - this just
  'bundles' related form elements together in a div tag and returns the Div obj
  """
  def __init__(self, element, label=None, add_elements=None, **kwargs):
    super().__init__(**kwargs)
    self.children = []
    if label:
      self.children.append(html.H6(label))
    self.children.append(element)
    if add_elements:
      self.children += add_elements
    self.children.append(html.Br())

class Bar(go.Bar):
  def __init__(self, x, y, colors, 
               name=None, text=None, textposition="outside", **kwargs):
    super().__init__(
      x=x, y=y,
      hoverinfo="x+y",
      marker=dict(color=colors))
    if text:
      self.update(text=text, textposition=textposition)
    if name:
      self.update(name=name)

class Scatter(go.Scatter):
  def __init__(self, x, y, color, name, size=8, mode="markers", **kwargs):
    super().__init__(
      x=x, y=y,
      hoverinfo="x+y",
      marker=dict(color=color, size=size),
      name=name,
      mode=mode,
      **kwargs)

### individual elements ###

class ShowsElement(FormElement):
  def __init__(self, elt_id):
    super().__init__(
      label="Show(s)",
      element=dcc.Dropdown(
        id=elt_id,
        options=get_form_options(["Bachelor", "Bachelorette"]),
        value=["Bachelor", "Bachelorette"],
        multi=True
      ))

class YearsElement(FormElement):
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

class RaceElement(FormElement):
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

###### app wide helper functions ######

def update_selected_years(years):
  """ shows user what the selected year range is """
  start, end = years
  return "Selected: ({start}, {end})".format(start=start, end=end)

def get_form_options(options_list):
  return [ {"label": x, "value": x} for x in options_list]

def get_race_color(flag):
  return {
    "white": COLORSCHEME[0],
    "nwhite": COLORSCHEME[1],
    True: COLORSCHEME[1],
    False: COLORSCHEME[0],
    "White": COLORSCHEME[0],
    "POC": COLORSCHEME[1],
    "hisp": COLORSCHEME[1],
    "afam": COLORSCHEME[2],
    "asn_paci": COLORSCHEME[3],
    "amin": COLORSCHEME[4],
    "mult": COLORSCHEME[5],
    "oth": COLORSCHEME[6]
  }.get(flag)

def get_ordered_race_flags(lst=None):
  order = ["white", "nwhite", "afam", "hisp", "asn_paci", "amin", "mult", "oth"]
  return sorted(lst, key=lambda x: order.index(x))
