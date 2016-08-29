#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy

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
        renderer.assets(self.get_assets())
        return str(renderer.render())
    return wrapper

#--------------------------------------------------------------------
page = compose(render, cherrypy.expose)

#--------------------------------------------------------------------
class BaseServer:
    def __init__(self, cherrypy_config, assets, auth):
        self._cherrypy_config = cherrypy_config
        self._assets = assets
        self._auth = auth

    def get_assets(self):
        return self._assets

    def get_auth(self):
        return self._auth

    def get_cherrypy_config(self):
        return self._cherrypy_config

    def start(self):
        cherrypy.quickstart(self, '/', self.get_cherrypy_config())

