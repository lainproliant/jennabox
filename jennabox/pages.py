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

#--------------------------------------------------------------------
class Page(PageRenderer):
    def body(self):
        return html.div(id='content')(
            self.header(),
            self.nav(),
            self.content())
    
    def header(self):
        return Header().render()

    def nav(self):
        return BasicLeftNav().render()

    def content(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class HomePage(Page):
    def content(self):
        return html.h1('I love you Jenna!')
