#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import os

#--------------------------------------------------------------------
class RenderFilter:
    def process(self, renderer):
        pass
    
    def __call__(self, render_f):
        def render_f_impl(*args, **kwargs):
            renderer = render_f(*args, **kwargs)
            self.process(renderer)
            return str(renderer.render())
        return render_f_impl

#--------------------------------------------------------------------
class AssetInjector(RenderFilter):
    def __init__(self, *assets):
        self._assets = assets
        
    def process(self, renderer):
        for asset in self._assets:
            ext = os.path.splitext(asset)[1]
            if ext == '.js':
                renderer.js(asset)
            elif ext == '.css':
                renderer.css(asset)
            else:
                raise ValueError('Unknown asset extension: %s' % asset)
        return renderer

