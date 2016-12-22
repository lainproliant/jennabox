#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import inspect
import os

from xeno import inject

from .markup import markup

#--------------------------------------------------------------------
def before(f):
    f.before = True
    return f

#--------------------------------------------------------------------
def require(*rights):
    def decorator(f):
        def require_f(self, *args, **kwargs):
            user = self.auth.get_user()
            user.require_rights(rights)
            return f(self, *args, **kwargs)
        return require_f
        if hasattr(f, 'exposed'):
            require_f.exposed = f.exposed
    return decorator

#--------------------------------------------------------------------
def render(f):
    def render_f(self, *args, **kwargs):
        renderer = f(self, *args, **kwargs)
        self.injector.inject(renderer)
        return str(renderer.render())
    if hasattr(f, 'exposed'):
        render_f.exposed = f.exposed
    return render_f

#--------------------------------------------------------------------
def server(cls):
    @inject
    def inject_deps(self, injector, log, cherrypy_config, auth, dao_factory):
        self.injector = injector
        self.cherrypy_config = cherrypy_config
        self.auth = auth
        self.dao_factory = dao_factory
        self.log = log

    cls._pre_handlers = []

    @before
    def clear_local_storage(self, *args, **kwargs):
        ThreadLocalStorage().clear()

    def start(self):
        cherrypy.quickstart(self, '/', self.cherrypy_config)

    def before_impl(self, *args, **kwargs):
        for f in cls._pre_handlers:
            f(self, *args, **kwargs)

    setattr(cls, '_before_impl', before_impl)
    setattr(cls, '_inject_deps', inject_deps)
    setattr(cls, 'start', start)

    def supported_method(f):
        def supported_f(self, *args, **kwargs):
            self._before_impl(self, *args, **kwargs)
            return f(self, *args, **kwargs)
        if hasattr(f, 'exposed'):
            supported_f.exposed = f.exposed
        return supported_f

    for name, f in inspect.getmembers(cls, predicate=callable):
        if hasattr(f, 'exposed') and f.exposed:
            setattr(cls, name, supported_method(f))

        if hasattr(f, 'before'):
            cls._pre_handlers.append(f)

    cls._pre_handlers.insert(0, clear_local_storage)
    return cls

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

    def items(self):
        return cherrypy.thread_data.thread_local_storage.items()

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

