import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import os

from app import app
from apps import index, rep, perf, notes, four_oh_four

# define base template for application
with open("templates/base.html", "r") as fl:
  base_template = fl.read()
app.index_string = base_template

# defining general layout
app.layout = html.Div([
  dcc.Location(id="url", refresh=False),
  html.Div(id="page-content"),
])

# creating static content routes
image_dir = "static"
image_exts = [".png", ".jpeg", ".jpg"]
valid_images = [os.path.basename(x) for x in os.listdir(image_dir)
  if os.path.splitext(x)[1] in image_exts]
static_image_route = "static/img"

# Add a static image route that serves images from desktop
@app.server.route("/{route}/<image_name>".format(route=static_image_route))
def serve_image(image_name):
  if image_name not in valid_images:
    raise Exception(
      '"{}" is excluded from the allowed static files'.format(image_name))
  return flask.send_from_directory(image_dir, image_name)

# display pages based on url
@app.callback(Output("page-content", "children"),
  [Input("url", "pathname")])
def display_page(pathname):
  pathname = pathname.strip("/") if pathname else None
  paths = {
    "": index.layout,
    "representation": rep.layout,
    "performance": perf.layout,
    "notes": notes.layout
  }
  return paths.get(pathname, four_oh_four.layout)

# run app
if __name__ == "__main__":
  app.run_server(debug=True)