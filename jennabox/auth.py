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
from xenum import *

from .domain import *

#--------------------------------------------------------------------
TOKEN_COOKIE = 'jennabook_login'

#--------------------------------------------------------------------
def require(*rights):
    def decorator(f):
        def require_f(self, *args, **kwargs):
            user = self.auth.get_user()
            user.require_rights(rights)
            return f(self, *args, **kwargs)
        return require_f
    return decorator

#--------------------------------------------------------------------
def random_password(length = 10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

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
    def __init__(self, log, dao_factory, expiry_timedelta, hash_rounds):
        self.log = log
        self.dao_factory = dao_factory
        self.expiry_timedelta = expiry_timedelta
        self.hash_rounds = hash_rounds

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

    def logout(self, login):
        login_dao = self.dao_factory.get_login_dao()
        login_dao.drop(login.token)
        cherrypy.thread_data.current_user = None
        raise cherrypy.HTTPRedirect('/')

    def change_password(self, user, old_password, new_password):
        if bcrypt.verify(old_password, user.passhash):
            user.remove_attribute(UserAttribute.PASSWORD_RESET_REQUIRED)
            user.passhash = self.encrypt_password(password)
            user_dao = self.dao_factory.get_user_dao()
            user_dao.put(user)
            raise cherrypy.HTTPRedirect('/')
        else:
            raise LoginFailure()

    def encrypt_password(self, password):
        return bcrypt.encrypt(password, rounds = self.hash_rounds)

    def get_login(self, token = None):
        if token is None:
            token = self._read_cookie_token()

        if token is None:
            return None

        login_dao = self.dao_factory.get_login_dao()
        login = login_dao.get(token)
        if login is not None and login.is_valid():
            return login
        else:
            return None

    def get_user(self, login = None):
        if not hasattr(cherrypy.thread_data, 'current_user'):
            if login is None:
                login = self.get_login()

            if login is not None:
                user_dao = self.dao_factory.get_user_dao()
                cherrypy.thread_data.current_user = user_dao.get(login.username)
            else:
                return User.GUEST

        return cherrypy.thread_data.current_user
    
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

