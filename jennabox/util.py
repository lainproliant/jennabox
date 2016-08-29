#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import threading

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
class AssetInjector:
    def __init__(self, *assets):
        self._assets = assets

    def __call__(self, f):
        def inject(*args, **kwargs):
            renderer = f(*args, **kwargs)
            renderer.assets(self._assets)
            return renderer
        return inject

#--------------------------------------------------------------------
class RenderInvoker:
    def __call__(self, f):
        def inject(*args, **kwargs):
            return str(f(*args, **kwargs).render())
        return inject

