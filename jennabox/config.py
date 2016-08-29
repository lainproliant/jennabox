#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
from xeno import *

#--------------------------------------------------------------------
class ServerModule:
    @provide
    @singleton
    def assets(self):
        return [
            '/static/font-awesome/css/font-awesome.css',
            '/static/css/minimal.css',
            '/static/css/jennabox.css',
            '/static/css/elements.css'
        ]

    @provide
    @singleton
    def expiry_timedelta(self):
        return timedelta(days = 1)
    
    @provide
    @singleton
    def cherrypy_config(self):
        return {
            '/': {
                'tools.staticdir.root':     os.path.abspath(os.getcwd())
            },
            '/static': {
                'tools.staticdir.on':       True,
                'tools.staticdir.dir':      'static'
            },
            '/images': {
                'tools.staticdir.on':       True,
                'tools.staticdir.dir':      '/opt/jennabox/images'
            }
        }
