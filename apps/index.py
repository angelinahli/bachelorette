import dash_core_components as dcc
import dash_html_components as html

from app import app
from utils import BSContainer

main_content = html.Div(
    className="text-center",
    children=[
        html.Img(
            id="postcard-title",
            className="img-fluid",
            src="/static/postcard_title.png",
            alt="The Bachelor & Race"
        )
    ]
)

layout = BSContainer(main_content=main_content)
