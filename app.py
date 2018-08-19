# Main module to run dash app
import dash
from dash.dependencies import Input, Output
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
image_dir = "static/img"
image_exts = [".png", ".jpeg", ".jpg"]
valid_images = [os.path.basename(x) for x in os.listdir(image_dir)
    if os.path.splitext(x)[1] in image_exts]
static_image_route = "/static/img"

# Add a static image route that serves images from desktop
@app.server.route("/{route}/<image_name>".format(route=static_image_route))
def serve_image(image_name):
    if image_name not in valid_images:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(image_name))
    return flask.send_from_directory(image_dir, image_name)

# put import statement here to avoid circular imports
from apps import index, numbers

# display pages based on url
@app.callback(Output("page-content", "children"),
    [Input("url", "pathname")])
def display_page(pathname):
    pathname = pathname.strip("/") if pathname else None
    paths = {
        "": index.layout,
        "the-numbers": numbers.layout,
    }
    # TODO change default behavior to return 404 error
    return paths.get(pathname, index.layout)

# run app
if __name__ == "__main__":
    app.run_server(debug=True)