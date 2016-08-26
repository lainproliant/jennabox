#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from indent_tools import html
from .renderer import Renderer, PageRenderer
from .components import *
from .markup import markup

#--------------------------------------------------------------------
class Page(PageRenderer):
    def body(self):
        return html.div(id = 'content')({'class': 'container'})(
            self.header(),
            html.div({'class': 'row'})(
                self.nav(),
                self.content()))
    
    def header(self):
        return Header().render()

    def nav(self):
        return BasicLeftNav().render()

    def content(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class HomePage(Page):
    def content(self):
        return html.div({'class': 'col-10'})(
            html.h1('I love you Jenna!'))
