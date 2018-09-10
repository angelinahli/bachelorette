import dash_core_components as dcc
import dash_html_components as html

import utils
from app import app

class BSCard(html.Div):
  def __init__(self, bg_color="", title=None, title_link=None, subtitle=None, 
               body_contents=[]):
    super().__init__(self, 
      className="card border-white bg-{}".format(bg_color))
    
    self.children = []
    body = html.Div(className="card-body", children=[])
    if title:
      title_obj = html.H5(title, className="card-title")
      if title_link:
        title_obj = html.A(title_obj, href=title_link)
      body.children.append(title_obj)
    if subtitle:
      subt_obj = html.H6(subtitle, className="card-subtitle text-muted")
      body.children.append(subt_obj)
      body.children.append(html.Br())
    if body_contents:
      body.children += body_contents
    self.children.append(body)

title = "The Bachelor & Race"
subtitle = "An Investigative Data Journalism Project"

main_content = html.Div(
  children=html.Div([
    BSCard(
      title="1. Representation",
      title_link="/representation",
      subtitle="Does the Bachelor/ette have a representation problem?",
      body_contents=[
        html.P([
          "The first part of this investigation centers around answering ",
          "the following questions:"]),
        html.Ul([
          html.Li([
            "How many POC contestants and leads are there compared to white ",
            "contestants and leads?"]),
          html.Li([
            "How has the percentage of POC contestants on the show changed ",
            "over time?"]),
          html.Li([
            "How does the percentage of POC contestants on the show compare ",
            "to the percentage of people of color in the American Population?"])
        ])
      ]),
    BSCard(
      title="2. Performance",
      title_link="/performance",
      subtitle="How well do POC Bachelor/ette contestants fare on the show?",
      body_contents=[
        html.P([
          "The second part of this investigation centers around answering ",
          "the following questions:"]),
        html.Ul([
          html.Li([
            "How long into a season do POC contestants last compared to their ",
            "white counterparts?"]),
          html.Li([
            "xxxxx?"])
        ])
      ]),
    BSCard(
      title="3. Conclusion & Notes",
      title_link="/notes",
      subtitle="The Bachelor franchise has a lot to improve on.",
      body_contents=[
        
      ])
  ])
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)
