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
class JennaBoxServer:
    def __init__(self):
        pass
    
    @cherrypy.expose
    def index(self):
        page = HomePage()
        page.js('test.js')
        return str(page.render())

    @cherrypy.expose
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
