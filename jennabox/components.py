#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from indent_tools import html
from .renderer import Renderer
from .markup import markup

#--------------------------------------------------------------------
class Header(Renderer):
    def render(self):
        return html.div(id='header')(html.h1('JennaBox'))

#--------------------------------------------------------------------
class SearchForm(Renderer):
    def render(self):
        return html.form(action='/search', method='get')(
            markup.text_input('query', placeholder='Search with tags'),
            markup.submit_button())

#--------------------------------------------------------------------
class BasicLeftNav(Renderer):
    def render(self):
        return html.div(id='left-nav')(SearchForm().render())

