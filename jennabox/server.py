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
from xeno import *

from .auth import AuthModule
from .config import ServerModule
from .dao import DaoModule
from .framework import BaseServer, page
from .pages import HomePage, LoginPage

#--------------------------------------------------------------------
class JennaBoxServer(BaseServer):
    def __init__(self, assets, auth, cherrypy_config):
        super().__init__(cherrypy_config, assets, auth)

    @page
    def index(self):
        return HomePage()

    @page
    def search(self, query):
        pass

    @page
    def login(self):
        return LoginPage()

#--------------------------------------------------------------------
def main():
    injector = Injector(ServerModule(), DaoModule(), AuthModule())
    server = injector.create(JennaBoxServer)
    server.start()

#--------------------------------------------------------------------
if __name__ == '__main__':
    main()

