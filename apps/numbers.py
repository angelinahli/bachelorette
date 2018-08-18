import dash_core_components as dcc
import dash_html_components as html

from app import app, base_template

layout = base_template.render_template(
    title_text="Part 1: Does the Bachelor/ette have a representation problem?",
    subtitle_text="..Yes. Here are the numbers."
)