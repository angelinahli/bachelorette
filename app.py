# Main module to run dash app
import dash
import dash_core_components as dcc
import dash_html_components as html

import flask
import os

server = flask.Flask("app")
app = dash.Dash(server=server)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

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
app.image_dir = "static/img"
list_image_exts = [".png", ".jpeg", ".jpg"]
app.list_of_images = [os.path.basename(x) for x in os.listdir(app.image_dir)
    if os.path.splitext(x)[1] in list_image_exts]
app.static_image_route = "/static/img"

import routes

# run app
if __name__ == "__main__":
    app.run_server(debug=True)