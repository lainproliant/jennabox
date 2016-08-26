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
        return html.header(html.h1(
            markup.icon('camera-retro'),
            'JennaBox'))

#--------------------------------------------------------------------
class SearchForm(Renderer):
    def render(self):
        return html.form(action='/search', method='get')({'class': 'search-form'})(
            markup.text_input('query', placeholder='Search with tags'),
            markup.submit_button())

#--------------------------------------------------------------------
class BasicLeftNav(Renderer):
    def render(self):
        return html.div(id='left-nav')({'class': 'col-2'})(
            html.div({'class': 'row'})(
                SearchForm().render()))

