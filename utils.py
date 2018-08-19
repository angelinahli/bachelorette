import dash_html_components as html

class BSContainer(html.Div):

    def __init__(self, main_content=None, title=None, subtitle=None, **kwargs):

        super().__init__(className="container", **kwargs)
        self.children = []

        # adding in title
        if title:
            self.children.append( html.H1(className="mt-5", children=title) )

        # adding sub title text
        if subtitle:
            self.children.append( html.P(className="lead", children=subtitle) )

        # adding body content
        if main_content:
            self.children.append(main_content)