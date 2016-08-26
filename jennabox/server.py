#!/usr/bin/env python3
#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import os

from .util import AssetInjector
from .pages import *

#--------------------------------------------------------------------
class JennaBoxConfig:
    def get_cherrypy_config(self):
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

#--------------------------------------------------------------------
assets = AssetInjector(
    '/static/font-awesome/css/font-awesome.css',
    '/static/minimal-css/minimal.css',
    '/static/css/jennabox.css'
)

#--------------------------------------------------------------------
class JennaBoxServer:
    def __init__(self):
        pass

    @cherrypy.expose
    @assets
    def index(self):
        return HomePage()

    @cherrypy.expose
    @assets
    def search(self, query):
        pass

#--------------------------------------------------------------------
def main():
    config = JennaBoxConfig()
    server = JennaBoxServer()

    cherrypy.quickstart(server, '/', config.get_cherrypy_config())

#--------------------------------------------------------------------
if __name__ == '__main__':
    main()
