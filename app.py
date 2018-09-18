# Main module to run dash app
import dash
import flask
import os

server = flask.Flask("app")
server.secret_key = os.environ.get("SECRET_KEY", "secret")
app = dash.Dash(server=server)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config["suppress_callback_exceptions"] = True