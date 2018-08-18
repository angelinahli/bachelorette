# @author Angelina Li
# @modified 8/16/2018
# @filename templates.py
# @description Collection of Dash objects used in main app

import dash
import dash_core_components as dcc
import dash_html_components as html

class BootstrapBase(object):
    """
    Creates a 'base' template that can be used to format different 
    pages in a multi-page app
    """

    def __init__(self, nav_brand=None, nav_items=[], 
                 default_title=None, default_subtitle=None,
                 default_footer=None):
        """
        nav_brand can be either a tuple or a dcc object
        """
        self.nav_brand = nav_brand
        self.nav_items = nav_items
        self.default_title = default_title
        self.default_subtitle = default_subtitle
        self.default_footer = default_footer
        
        self.navbar = self._get_navbar()

    def _get_navbar(self):
        """ returns an html.Nav object that is the navbar """
        navbar = html.Nav(className="navbar navbar-expand-md navbar-light")
        navbar.children = []

        if self.nav_brand != None:
            if isinstance(self.nav_brand, tuple):
                url, text = self.nav_brand
                nav_brand_obj = html.A(text, className="navbar-brand", href=url)
            else:
                nav_brand_obj = self.nav_brand
            navbar.children.append(nav_brand_obj)

        if self.nav_items:
            nav_item_bar = html.Ul(className="nav navbar-nav pull-right")
            nav_item_bar.children = []
            for url, text in self.nav_items:
                nav_item_obj = html.Li(
                    className="nav-item",
                    children=html.A(
                        text, className="nav-link", href=url))
                nav_item_bar.children.append(nav_item_obj)
            navbar.children.append(nav_item_bar)

        return navbar

    def render_template(self, main_content=None, title_text=None, 
                        subtitle_text=None, footer_text=None,
                        suppress_navbar=None):
        """
        Returns an html.Div 'container' containing a standardized navbar 
        (if applicable) and 
        """
        container = html.Div(className="container")
        container.children = []

        if not suppress_navbar:
            container.children.append(self.navbar)

        title = title_text or self.default_title
        if title:
            container.children.append(html.H1(title, className="mt-5"))

        subtitle = subtitle_text or self.default_subtitle
        if subtitle:
            container.children.append(html.P(subtitle, className="lead"))

        if main_content:
            container.children.append(main_content)

        footer = footer_text or self.default_footer
        if footer:
            footer_obj = html.Div(
                children=footer, 
                className="footer text-muted text-center")
            container.children.append(footer_obj)

        return container