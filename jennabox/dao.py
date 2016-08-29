#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import collections
import os
import sqlite3

from datetime import datetime
from xeno import *
from .dao import *

#--------------------------------------------------------------------
class DaoModule:
    @provide
    @singleton
    def sqlite_file(self):
        return 'jennabox.sqlite'

    @provide
    @singleton
    def sqlite_ddl_file(self):
        return 'jennabox.sql'

    @provide
    @singleton
    def login_cache(self):
        return {}

    @provide
    def db_conn(self, sqlite_file, sqlite_ddl_file):
        if not hasattr(cherrypy.thread_data, 'db_conn'):
            if not os.path.exists(sqlite_file):
                with sqlite3.connect(sqlite_file) as db:
                    with open(sqlite_ddl_file, 'rt') as infile:
                        db.execute(infile.read())
            cherrypy.thread_data.db_conn = sqlite3.connect(sqlite_file)
        return cherrypy.thread_data.db_conn

    @provide
    def dao_factory(self, injector):
        return SqliteDaoFactory(injector)

#--------------------------------------------------------------------
class SqliteDaoFactory:
    def __init__(self, injector):
        self.injector = injector

    def get_user_dao(self):
        return self.injector.create(SqliteUserDao)

    def get_login_dao(self):
        return self.injector.create(InMemoryLoginDao)

#--------------------------------------------------------------------
class InMemoryLoginDao:
    def __init__(self, login_cache):
        self.cache = login_cache
        
    def load_login(self, username, valid = True):
        if username in self.cache:
            return self.cache.get(username)
        else:
            return None

    def save_login(self, login):
        self.cache[login.username] = login

    def drop_login(self, username):
        del self.cache[username]

#--------------------------------------------------------------------
class SqliteUserDao:
    def __init__(self, db_conn):
        self.db = db_conn
    
    def load_user(self, username):
        users = self.load_users([username])
        if users:
            return users[0]
        else:
            return None

    def load_users(self, usernames):
        self.db.execute('select * from users where username in %s' % (','.join('?' * len(usernames))), usernames)
        user_map = collections.OrderedDict()
        for row in self.db.fetchall():
            user = User(*row)
            user_map[user.username] = user

        self.db.execute('select * from user_rights where username in %s' % (','.join('?' * len(usernames))), usernames)
        for row in self.db.fetchall():
            username, right = row
            if username in user_map:
                user_map[username].rights.append(right)

        return user_map.values()

    def save_user(self, user):
        self.db.execute('insert or replace into users (username, passhash) values (?, ?)', (user.username, user.passhash))
        self.db.execute('delete from user_rights where username = ?', (user.username,))
        for right in user.rights:
            self.db.execute('insert into user_rights (username, right) values (?, ?)', (user.username, right))

