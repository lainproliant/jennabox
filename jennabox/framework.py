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
def jennabox_server():
    handler = cherrypy.serving.request.handler
    if hasattr(handler, 'callable'):
        server = handler.callable.__self__
        if hasattr(server, 'before') and callable(server.before):
            server.before()

cherrypy.tools.jennabox_server = cherrypy.Tool('on_start_resource', jennabox_server)

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
        ThreadLocalStorage().clear()

#--------------------------------------------------------------------
class ThreadLocalStorage:
    """
        A wrapper class around CherryPy thread local storage.
    """

    def __init__(self):
        if not hasattr(cherrypy.thread_data, 'thread_local_storage'):
            self.clear()

    def clear(self):
        cherrypy.thread_data.thread_local_storage = {}

    def remove(self, key):
        del cherrypy.thread_data.thread_local_storage[key]

    def contains(self, key):
        return key in cherrypy.thread_data.thread_local_storage

    def get(self, key, default = None):
        if self.contains(key):
            return cherrypy.thread_data.thread_local_storage[key]
        else:
            return default

    def put(self, key, value):
        cherrypy.thread_data.thread_local_storage[key] = value

#--------------------------------------------------------------------
class Cookies:
    """
        A wrapper around cherrypy request cookies.
    """
    
    def __init__(self, request = None, response = None):
        self.request = request or cherrypy.request
        self.response = response or cherrypy.response

    def exists(self, cookie):
        return cookie in self.request.cookie

    def get(self, cookie):
        if self.exists(cookie):
            return self.request.cookie[cookie].value
        else:
            return None

    def put(self, cookie, value, path = '/', max_age = None, version = 1):
        self.response.cookie[cookie] = value
        self.response.cookie[cookie]['path'] = path
        self.response.cookie[cookie]['version'] = version

        if max_age is not None:
            self.response.cookie[cookie]['max-age'] = max_age

#--------------------------------------------------------------------
class Renderer:
    def render(self):
        raise NotImplementedError()

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

