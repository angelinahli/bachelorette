# Main module to run dash app

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import os
import pandas as pd
import plotly.graph_objs as go

########## initialize Dash app ##########

server = flask.Flask("app")
app = dash.Dash(server=server)

########## designing general ui ##########

class BootstrapContainer(html.Div):
    """
    Blueprint for the app layout - 'wrapper' around data content
    """
    DEFAULT_FOOTER = "Angelina Li 2018 ©"

    def __init__(self, main_content=None, title_text=None, subtitle_text=None,
                footer_text=None, suppress_footer=False):
        super().__init__(className="container")

        self.children = []

        # adding in title
        if title_text:
            title = html.H1(className="mt-5", children=title_text) 
            self.children.append(title)

        # adding sub title text
        if subtitle_text:
            subtitle = html.P(className="lead", children=subtitle_text) 
            self.children.append(subtitle)

        # adding body content
        if main_content:
            self.children.append(main_content)

        # adding footer
        if not suppress_footer:
            footer_text = footer_text or self.DEFAULT_FOOTER
            footer = html.Div(
                className="footer text-muted text-center",
                children=footer_text)
            self.children.append(footer)

########## designing general ui ##########
if __name__ == "__main__":
    app.layout = BootstrapContainer(
        title_text="Testing", 
        subtitle_text="Another line"
    )
    app.run_server(debug=True)