import dash_core_components as dcc
import dash_html_components as html

import utils
from app import app

title = "The Bachelor & Race"
subtitle = "An Investigative Data Journalism Project"

main_content = html.Div(
  children=[
    html.A(
      href="https://www.washingtonpost.com/news/wonk/wp/2015/02/04/the-bachelor-is-embarrassingly-white/",
      target="_blank",
      children=html.H4("In short, the Bachelor franchise has a race problem.")),
    html.Br(),
    html.H5(
      """
      Many have criticized the Bachelor/ette franchise for failing to
      adequately represent people of color in its casting. This interactive
      application aims to evaluate those criticisms head on.
      """),
    html.Br(),
    html.H5(
      """
      The first part of this interactive application examines the presence 
      (or lack thereof) of POC on the frachise.
      The second part tracks how POC candidates fare after being selected.
      """),
    html.Br(),
    html.Img(
      src="/static/bachelor_meme.jpg",
      className="img-fluid mx-auto d-block",
      alt="Tonight... on the most dramatic episode of the Bachelor"),
    html.P("Source: memes.90dev.com", className="text-muted text-center")
  ]
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)
