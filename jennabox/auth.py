#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from xeno import *

#--------------------------------------------------------------------
TOKEN_COOKIE = 'jennabook_login'

#--------------------------------------------------------------------
class LoginFailure(Exception):
    pass

#--------------------------------------------------------------------
class AccessDenied(Exception):
    pass

#--------------------------------------------------------------------
def require(f, *rights):
    def wrapper(self, *args, **kwargs):
        self.get_auth().require_rights(rights)
        return f(self, *args, **kwargs)

#--------------------------------------------------------------------
class AuthModule:
    @provide
    def auth(self):
        return DummyAuth()
        
#--------------------------------------------------------------------
class AuthProvider:
    def __init__(self, dao_factory):
        self.dao_factory = dao_factory

    def validate_session(self):
        token = self._read_cookie_token()
        if token is None:
            return None

        login_dao = dao_factory.get_login_dao()
        # TODO put stuff here



