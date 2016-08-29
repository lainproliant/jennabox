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
from .dao import *

#--------------------------------------------------------------------
SQL_DDL_FILE = 'jennabox.sql'

#--------------------------------------------------------------------
class DaoSessionFactoryImpl(DaoSessionFactory):
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self.dao_ctor_map = {}
        self.
        self.dao_ctor_map['user'] = lambda: SqliteUserDao()
        self.dao_ctor_map['login'] = lambda

    def get(self):
        return SqliteDaoSession(sqlite_file)

#--------------------------------------------------------------------
class SqliteDaoSession(DaoSession):
    def __init__(self, sqlite_file, login_dao):
        self.sqlite_file = sqlite_file
        self.login_dao = login_dao
        self.db = None

    def get_user_dao(self):
        return SqliteUserDao(self.db)

    def __enter__(self):
        if not os.path.exists(self.sqlite_file):
            self._init_db()
        self.db = sqlite3.connect(self, sqlite_file)

    def __exit__(self):
        self.db.close()

    def _init_db(self):
        with sqlite3.connect(self.sqlite_file) as db:
            with open(self.sqlite_file, 'rt') as infile:
                db.execute(infile.read())

#--------------------------------------------------------------------
class InMemoryLoginDao(LoginDao):
    def __init__(self):
        self.cache = collections.defaultdict(list)
        
    def load_logins(self, username, valid = True):
        if username in self.cache:
            return self.cache.get(username)
        else:
            return []

    def save_login(self, login):
        self.cache[login.username].append(login)

    def drop_logins(self, username):
        del self.cache[username]

#--------------------------------------------------------------------
class SqliteUserDao(UserDao):
    def __init__(self, db):
        self.db = db
    
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

