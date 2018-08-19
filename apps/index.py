import dash_core_components as dcc
import dash_html_components as html

from app import app
from utils import BSContainer

title = "The Bachelor & Race"
subtitle = "An Investigative Data Journalism Project"

main_content = html.Div(
    className="text-center",
    children=[

    ]
)

layout = BSContainer(
    title=title,
    subtitle=subtitle,
    main_content=main_content)
