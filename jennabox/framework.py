#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
from xeno import inject

#--------------------------------------------------------------------
def compose(*decorators):
    """
    Compose multiple decorators into a single decorator.
    """
    def composed(f):
        for dec in decorators:
            f = dec(f)
        return f
    return composed

#--------------------------------------------------------------------
def render(f):
    def wrapper(self, *args, **kwargs):
        renderer = f(self, *args, **kwargs)
        self.injector.inject(renderer)
        renderer.assets(self.assets)
        return str(renderer.render())
    return wrapper

#--------------------------------------------------------------------
page = compose(render, cherrypy.expose)

#--------------------------------------------------------------------
class BaseServer:
    @inject
    def inject_deps(self, injector, cherrypy_config, auth, assets):
        self.injector = injector
        self.cherrypy_config = cherrypy_config
        self.auth = auth
        self.assets = assets

    @inject
    def set_auth(self, auth):
        self.auth = auth

    @inject
    def set_cherrypy_config(self, cherrypy_config):
        self.cherrypy_config = cherrypy_config

    def start(self):
        cherrypy.quickstart(self, '/', self.cherrypy_config)

