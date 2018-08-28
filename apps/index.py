import dash_core_components as dcc
import dash_html_components as html

import utils
from app import app

title = "The Bachelor & Race"
subtitle = "An Investigative Data Journalism Project"

main_content = html.Div(
  className="text-center",
  children=[]
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)
