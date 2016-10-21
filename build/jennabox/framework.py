#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import os

from xeno import inject

from .markup import markup

#--------------------------------------------------------------------
def render(f):
    def render_f(self, *args, **kwargs):
        self.before(self, *args, **kwargs)
        renderer = f(self, *args, **kwargs)
        self.injector.inject(renderer)
        return str(renderer.render())
    return render_f

#--------------------------------------------------------------------
class BaseServer:
    @inject
    def inject_deps(self, injector, cherrypy_config, auth, dao_factory):
        self.injector = injector
        self.cherrypy_config = cherrypy_config
        self.auth = auth
        self.dao_factory = dao_factory

    def start(self):
        cherrypy.quickstart(self, '/', self.cherrypy_config)

    def before(self, *args, **kwargs):
        pass

#--------------------------------------------------------------------
class Renderer:
    def render(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class HTML(Renderer):
    def __init__(self, *elements):
        self.elements = elements

    def render(self):
        return self.elements

#--------------------------------------------------------------------
class AssetList(Renderer):
    def __init__(self):
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

    def render(self):
        return ([markup.js(js) for js in self._js_files] +
                [markup.css(css) for css in self._css_files])

