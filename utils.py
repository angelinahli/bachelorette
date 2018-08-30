import dash_core_components as dcc
import dash_html_components as html

PRIMARY_COLOR = "#C95B83"
COLORSCHEME = ["#C95B83", "#FFBD4A", "#F26B3C", "#399E5A", "#5AB1BB", "#1446A0", 
               "#731963"]

class BSContainer(html.Div):
  def __init__(self, main_content=None, title=None, subtitle=None, **kwargs):

    super().__init__(className="container", **kwargs)
    self.children = []

    # adding in title
    if title:
      self.children.append( html.H1(className="mt-5", children=title) )

    # adding sub title text
    if subtitle:
      self.children.append( html.P(className="lead", children=subtitle) )

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

class BSButton(html.Button):
  def __init__(self, btn_type="btn-outline-dark", **kwargs):
    super().__init__(**kwargs)
    self.className = "btn " + btn_type

class FormElement(html.Div):
  """ 
  Dash doesn't package form elements with labels nicely yet - this just
  'bundles' related form elements together in a div tag and returns the Div obj
  """
  def __init__(self, label, element, add_elements=None, **kwargs):
    super().__init__(**kwargs)
    self.children = [html.H6(label), element]
    if add_elements:
      self.children += add_elements
    self.children.append(html.Br())

def get_form_options(options_list):
  return [ {"label": x, "value": x} for x in options_list]

def get_colors(items_list):
  colors = COLORSCHEME
  if len(colors) < len(items_list):
    colors += [PRIMARY_COLOR for _ in range(len(items_list) - len(colors))]
  return dict(zip(items_list, colors))
