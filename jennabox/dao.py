#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import uuid

#--------------------------------------------------------------------
class DaoSessionFactory:
    def get(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class DaoSession:
    def get_user_dao(self):
        raise NotImplementedError()

    def get_login_dao(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class User:
    def __init__(self, username, passhash, rights = None):
        self.username = username
        self.passhash = passhash
        self.rights = rights or []

#--------------------------------------------------------------------
class Login:
    def __init__(self, username, token = None, valid = 1, expiry_dt = None):
        self.username = username
        self.token = token or uuid.uuid4()
        self.valid = valid
        self.expiry_dt = expiry_dt

#--------------------------------------------------------------------
class LoginDao:
    def load_logins(self, username, valid = True):
        raise NotImplementedError()

    def save_login(self, login):
        raise NotImplementedError()

#--------------------------------------------------------------------
class UserDao:
    def load_user(self, username):
        raise NotImplementedError()
    
    def load_users(self, usernames):
        raise NotImplementedError()

    def save_user(self, user):
        raise NotImplementedError()


