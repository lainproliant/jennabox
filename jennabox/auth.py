#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import random
import string

from passlib.hash import bcrypt
from datetime import datetime, timedelta
from xeno import *

from .domain import Login

#--------------------------------------------------------------------
TOKEN_COOKIE = 'jennabook_login'

#--------------------------------------------------------------------
class LoginFailure(Exception):
    pass

#--------------------------------------------------------------------
class AccessDenied(Exception):
    pass

#--------------------------------------------------------------------
def random_password(length = 10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

#--------------------------------------------------------------------
def require(f, *rights):
    def wrapper(self, *args, **kwargs):
        self.get_auth().require_rights(rights)
        return f(self, *args, **kwargs)

#--------------------------------------------------------------------
class AuthModule:
    @provide
    def auth(self, injector):
        return injector.create(AuthProvider)

    @provide
    @singleton
    def expiry_timedelta(self):
        return timedelta(days = 1)

    @provide
    @singleton
    def hash_rounds(self):
        return 12 # 2**12

#--------------------------------------------------------------------
class AuthProvider:
    def __init__(self, dao_factory, expiry_timedelta, hash_rounds):
        self.dao_factory = dao_factory
        self.expiry_timedelta = expiry_timedelta
        self.hash_rounds = hash_rounds

    @inject
    def inject_log(self, log):
        self.log = log

    def login(self, username, password):
        user_dao = self.dao_factory.get_user_dao()
        login_dao = self.dao_factory.get_login_dao()

        user = user_dao.get(username)
        if user is None:
            raise LoginFailure()
        if bcrypt.verify(password, user.passhash):
            login = Login(user.username, datetime.now() + self.expiry_timedelta)
            login_dao.put(login)
            self._write_cookie_token(login.token)
            raise cherrypy.HTTPRedirect('/')
        else:
            raise LoginFailure()

    def logout(self):
        login = self.validate_login()
        login_dao = self.dao_factory.get_login_dao()
        login_dao.drop(login.token)
        raise cherrypy.HTTPRedirect('/')

    def save_user(self, user, password):
        user.passhash = bcrypt.encrypt(password, rounds = self.hash_rounds)
        user_dao = self.dao_factory.get_user_dao()
        user_dao.put(user)

    def validate_login(self):
        token = self._read_cookie_token()
        if token is None:
            return None

        login_dao = self.dao_factory.get_login_dao()
        login = login_dao.get(token)
        if login is None or token != login.token or datetime.now() > login.expiry_dt:
            return None
        else:
            return login

    def get_current_user(self):
        login = self.validate_login()
        if login is not None:
            user_dao = self.dao_factory.get_user_dao()
            return user_dao.get(login.username)
        else:
            return None

    def _read_cookie_token(self):
        if TOKEN_COOKIE in cherrypy.request.cookie:
            return cherrypy.request.cookie[TOKEN_COOKIE].value
        else:
            return None

    def _write_cookie_token(self, token):
        cherrypy.response.cookie[TOKEN_COOKIE] = token
        cherrypy.response.cookie[TOKEN_COOKIE]['path'] = '/'
        cherrypy.response.cookie[TOKEN_COOKIE]['max-age'] = 60*60*24
        cherrypy.response.cookie[TOKEN_COOKIE]['version'] = 1

