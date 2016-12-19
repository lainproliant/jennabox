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
from getpass import getpass
from datetime import datetime, timedelta
from xeno import *
from xenum import *

from .framework import ThreadLocalStorage, Cookies
from .domain import *

#--------------------------------------------------------------------
TOKEN_COOKIE = 'jennabook_login'
CURRENT_USER = 'current_user'

#--------------------------------------------------------------------
def random_password(length = 10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

#--------------------------------------------------------------------
def input_password():
    while True:
        passA = getpass(prompt="Enter password: ")
        passB = getpass(prompt="Confirm password: ")

        if passA == passB:
            return passA
        else:
            print('Passwords do not match.  Please try again.')

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
        ThreadLocalStorage().remove(CURRENT_USER)
        raise cherrypy.HTTPRedirect('/')

    def change_password(self, user, old_password, new_password):
        if bcrypt.verify(old_password, user.passhash):
            user.remove_attribute(UserAttribute.PASSWORD_RESET_REQUIRED)
            user.passhash = self.encrypt_password(new_password)
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
        tls = ThreadLocalStorage()
        user = tls.get(CURRENT_USER)
        if user is None or (login is not None and user.username != login.username):
            if login is None:
                login = self.get_login()

            if login is not None:
                user_dao = self.dao_factory.get_user_dao()
                user = user_dao.get(login.username)
                tls.put(CURRENT_USER, user)
            else:
                user = User.GUEST

        return user

    def _read_cookie_token(self):
        return Cookies().get(TOKEN_COOKIE)

    def _write_cookie_token(self, token):
        Cookies().put(TOKEN_COOKIE, token, max_age = 60*60*24)

