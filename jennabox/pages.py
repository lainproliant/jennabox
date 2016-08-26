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
        return html.div({'class': 'container'})(
            self.header(),
            html.div({'class': 'row'})(
                html.div(id = 'nav')({'class': 'col-2'})(self.nav()),
                html.div(id = 'content')({'class': 'col-10'})(self.content())))
    
    def header(self):
        return Header().render()

    def nav(self):
        return BasicLeftNav().render()

    def content(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class HomePage(Page):
    def content(self):
        return html.div({'class': 'intro-box'})(
            html.h1('Welcome'),
            html.h3('JennaBox is a private image hosting and tagging site for you, your friends, and your family.'))

#--------------------------------------------------------------------
class LoginPage(Page):
    def content(self):
        return LoginForm().render()

