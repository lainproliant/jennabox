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

from datetime import timedelta

from .auth import DatabaseUserAuthProvider
from .dao_impl import SqliteDaoSessionFactory
from .pages import HomePage, LoginPage
from .util import compose, AssetInjector, RenderInvoker

#--------------------------------------------------------------------
class JennaBoxConfig:
    def __init__(self):
        self.session_factory = SqliteDaoSessionFactory(self.get_sqlite_file())

    def get_sqlite_file(self):
        return 'jennabox.sqlite'

    def get_expiry_timedelta(self):
        return timedelta(days = 1)

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
    
    def get_session(self):
        return self.session_factory.get()

    def session_factory(self):
        return SqliteDaoSessionFactory(self.config.get_sqlite_file())

#--------------------------------------------------------------------
class JennaBoxServer:
    render = RenderInvoker()
    inject = AssetInjector(
        '/static/font-awesome/css/font-awesome.css',
        '/static/css/minimal.css',
        '/static/css/jennabox.css',
        '/static/css/elements.css'
    )
    page = compose(inject, render, cherrypy.expose)
    config = JennaBoxConfig()
    auth = DatabaseUserAuthProvider(config)

    @page
    def index(self):
        return HomePage()

    @page
    def search(self, query):
        pass

    @page
    def login(self):
        return LoginPage()

    def start(self):
        cherrypy.quickstart(self, '/', self.config.get_cherrypy_config())

#--------------------------------------------------------------------
def main():
    server = JennaBoxServer()
    server.start()

#--------------------------------------------------------------------
if __name__ == '__main__':
    main()
