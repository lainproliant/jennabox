#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import os

from indent_tools import html
from .markup import markup

#--------------------------------------------------------------------
class Renderer:
    def __init__(self):
        self._component_map = {}

    def get_component(self, name):
        if not name in self._component_map:
            raise ValueError('Undefined component "%s".' % name)
        return self._component_map(name)

    def put_component(self, name, comp):
        self._component_map[name] = comp

    def render_component(self, name):
        return self.get_component(name).render()
    
    def render(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class PageRenderer(Renderer):
    def __init__(self):
        super().__init__()
        self._title = 'My Application'
        self._js_files = []
        self._css_files = []

    def js(self, src):
        self._js_files.append(src)
        return self

    def css(self, href):
        self._css_files.append(href)
        return self

    def asset(self, asset):
        ext = os.path.splitext(asset)[1]
            
        if ext == '.js':
            self._js_files.append(asset)
        elif ext == '.css':
            self._css_files.append(asset)
        else:
            raise ValueError('Unknown asset extension: %s' % asset)
        return self

    def assets(self, assets):
        for asset in assets:
            self.asset(asset)
        return self

    def title(self, title):
        self._title = title
        return self
    
    def body(self):
        raise NotImplementedError()

    def render(self):
        return html.html().doctype('html')(
                html.head(
                 html.title(self._title)),
                 [markup.js(x) for x in self._js_files],
                 [markup.css(x) for x in self._css_files],

                self.body())
