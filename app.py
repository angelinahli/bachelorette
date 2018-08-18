# Main module to run dash app

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import os

from templates import BootstrapBase

server = flask.Flask("app")
app = dash.Dash(server=server)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# define base template for application
nav_brand = html.A(
    href="/",
    children=html.Img(
        className="nav-brand img-fluid",
        src="static/long_title.png",
        alt="Bachelor & Race"
    )
)
base_template = BootstrapBase(
    nav_brand=("/", "Bachelor & Race"),
    nav_items=[
        ("/the-numbers/", "Representation")
    ],
    default_footer = u"© Angelina Li 2018"
)

# import placed here to prevent circular imports
from apps import index, numbers

image_dir = "static"
list_image_exts = [".png", ".jpeg", ".jpg"]
list_of_images = [os.path.basename(x) for x in os.listdir(image_dir)
    if os.path.splitext(x)[1] in list_image_exts]
static_image_route = "/static"

# defining general layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Add a static image route that serves images from desktop
@app.server.route( os.path.join(static_image_route, "<image_name>") )
def serve_image(image_name):
    if image_name not in list_of_images:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(image_name))
    return flask.send_from_directory(image_dir, image_name)

# display pages based on url
@app.callback(Output("page-content", "children"),
    [Input("url", "pathname")])
def display_page(pathname):
    if pathname:
        pathname = pathname.strip("/")
    paths = {
        "": index.layout,
        "the-numbers": numbers.layout,
    }
    # TODO change default behavior to return 404 error
    return paths.get(pathname, index.layout)

# run app
if __name__ == "__main__":
    app.run_server(debug=True)