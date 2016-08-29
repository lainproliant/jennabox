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
        name = f.__name__
        for dec in decorators:
            f = dec(f)
        f.__name__ = name
        return f
    return composed

#--------------------------------------------------------------------
def render(f):
    def wrapper(*args, **kwargs):
        renderer = f(*args, **kwargs)
        renderer.assets(f.__self__.get_assets())
        return str(renderer.render())
    return wrapper

#--------------------------------------------------------------------
page = compose(cherrypy.expose, render)

#--------------------------------------------------------------------
class BaseServer:
    def __init__(self, assets):
        self._assets = assets

    def get_assets(self):
        return self._assets

    def start(self):
        cherrypy.quickstart(self, '/', self.config.get_cherrypy_config())

