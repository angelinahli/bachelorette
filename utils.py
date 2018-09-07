import dash_core_components as dcc
import dash_html_components as html

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

LAYOUT_FONT = dict(font=dict(family="Karla"))
LAYOUT_ANN = dict(
    showarrow=False, 
    font=dict(color=SECONDARY_COLOR, size=14, family="Karla"))

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
      id="tabs",
      colors={"border": c_border, "primary": c_primary, "background": c_back},
      **kwargs)

class BSButton(html.Button):
  def __init__(self, btn_type="btn-outline-dark", **kwargs):
    super().__init__(**kwargs)
    self.className = "btn " + btn_type

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

def get_ordered_race_flags(lst):
  order = ["white", "nwhite", "afam", "hisp", "asn_paci", "amin", "mult", "oth"]
  return sorted(lst, key=lambda x: order.index(x))
