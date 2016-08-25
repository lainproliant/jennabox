#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from indent_tools import HtmlFactory

hf = HtmlFactory()

#--------------------------------------------------------------------
class Renderer:
    def __init__(self, title):
        self.default_title = title

    def main_template(self, title = None):
        return hf.html(
                hf.head(
                 hf.title(title or self.default_title)),
                hf.body(
                 self.header(),
                 self.top_nav(),
                 self.side_nav(),
                 self.content()))

    def header(self):
        return hf.div()

    def top_nav(self):
        return hf.div()

    def side_nav(self):
        return hf.div()

    def content(self):
        return hf.div()

    def render(self):
        return str(self.main_template())

#--------------------------------------------------------------------
class HomeRenderer(Renderer):
    def __init__(self):
        super().__init__('JennaBox <3')

