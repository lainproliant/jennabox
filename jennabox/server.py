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

from .auth import AuthModule, LoginFailure
from .config import ServerModule
from .dao import DaoModule
from .framework import BaseServer, page
from .content import *

#--------------------------------------------------------------------
class JennaBoxServer(BaseServer):
    @page
    def index(self):
        return Page(HomePage())

    @page
    def search(self, query):
        pass

    @page
    def login_page(self):
        return Page(LoginForm())

    @page
    def login(self, username, password):
        try:
            self.auth.login(username, password)
        except LoginFailure as e:
            return Page(LoginForm(failed = True))

    @page
    def logout(self):
        self.auth.logout()

    @inject
    def require_admin_user(self, admin_user):
        pass

    @inject
    def inject_auth(self, auth):
        self.auth = auth

#--------------------------------------------------------------------
def main():
    injector = Injector(ServerModule(), DaoModule(),
                        AuthModule(), ContentModule())
    server = injector.create(JennaBoxServer)
    server.start()

#--------------------------------------------------------------------
if __name__ == '__main__':
    main()

