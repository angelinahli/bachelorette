# Main module to run dash app
import dash
import flask

server = flask.Flask("app")
app = dash.Dash(server=server)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config["suppress_callback_exceptions"] = True