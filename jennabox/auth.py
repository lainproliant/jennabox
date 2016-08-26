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

#--------------------------------------------------------------------
TOKEN_COOKIE = 'jennabook_login'

#--------------------------------------------------------------------
class LoginFailure(Exception):
    pass

#--------------------------------------------------------------------
class AccessDenied(Exception):
    pass

#--------------------------------------------------------------------
class AuthInfo:
    def __init__(self, user, rights):
        self.user = user
        self.rights = rights

#--------------------------------------------------------------------
class AuthProvider:
    pass

#--------------------------------------------------------------------
class DatabaseUserAuthProvider(AuthProvider):
    def __init__(self, config):
        self.config = config
    
    def require(self, *rights):
        def decorator(f):
            def decorate(*args, **kwargs):
                rights_set = set(self.get_user().rights)
                for right in rights:
                    if not right in rights_set:
                        raise AccessDenied()
                return f(*args, **kwargs)
            return decorate
        return decorator

    def get_user(self):
        login = self._validate_session()
        if login is not None:
            with self._daos() as daos:
                user_dao = daos.get_user_dao()
                return user_dao.get_user(login.username)
        else:
            return None

    def login(self, username, password):
        with self._daos() as daos:
            user_dao = daos.get_user_dao()
            user = user_dao.get_user(username)
            if self._validate_password(self, password, user.passhash):
                pass
            else:
                raise LoginFailure(username)

    def logout(self):
        login = self.__validate_session()
        if login is not None:
            login.valid = 0
            with self._daos() as daos:
                login_dao = daos.get_login_dao()
                login_dao.save_login(login)

    def _write_cookie_token(self, auth_token):
        cherrypy.response.cookie[TOKEN_COOKIE] = auth_token
        cherrypy.resposne.cookie[TOKEN_COOKIE]['expires'] = self._cookie_expr_secs

    def _read_cookie_token(self):
        if TOKEN_COOKIE in cherrypy.response.cookie:
            return cherrypy.response.cookie[TOKEN_COOKIE].value
        elif TOKEN_COOKIE in cherrypy.request.cookie:
            return cherrypy.response.cookie[TOKEN_COOKIE].value
        else:
            return None
    
    def _create_login(self, user):
        return Login(user.username, expiry_dt = datetime.now() + config.get_expiry_timedelta())

    def _validate_session(self):
        token = self._read_cookie_token()
        if token is None:
            return None

        with self._daos() as daos:
            login_dao = daos.get_login_dao()
            login = login_dao.get_login(token)
            if login.valid and login.expiry_dt > datetime.now():
                return login
            else:
                return None

    def _validate_password(self, password, passhash):
        return bcrypt.verify(password, passhash)

    def _hash_password(self, password):
        return bcrypt.encrypt(password, rounds = self.config.get_password_rounds())

    def _daos(self):
        return self.config.get_daos()

    def get_rights(self):
        pass

