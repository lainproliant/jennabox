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

from xeno import inject, provide

#--------------------------------------------------------------------
class ContentModule:
    @provide
    def header(self, auth, dao_factory):
        user = auth.get_current_user()
        return Header(user) 

    @provide
    def nav(self):
        return BasicLeftNav()

#--------------------------------------------------------------------
class Page(PageRenderer):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def body(self):
        return html.div({'class': 'container'})(
            self.header.render(),
            html.div({'class': 'row'})(
                html.div(id = 'nav')({'class': 'col-2'})(self.nav.render()),
                html.div(id = 'content')({'class': 'col-10'})(self.content.render())))
    
    @inject
    def set_header(self, header):
        self.header = header
    
    @inject
    def set_nav(self, nav):
        self.nav = nav
    
    @inject
    def inject_content_deps(self, injector):
        injector.inject(self.content)

