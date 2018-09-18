import dash_core_components as dcc
import dash_html_components as html

import utils
from app import app

title = "404"
subtitle = "Something bad happened :("

main_content = html.Div(
  children=[
    html.A(
      href="/",
      children=html.H4("Take me back to safety")),
    html.Br(),
    html.Img(
      src="/static/sad_rachel.jpg",
      className="img-fluid mx-auto d-block",
      alt="Bachelorette Rachel is sad"),
    html.P("Source: ABC News", className="text-muted")
  ],
  className="text-center"
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)
