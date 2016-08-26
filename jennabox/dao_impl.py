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
class SqliteDaoSessionFactory(DaoSessionFactory):
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file

    def get(self):
        return SqliteDaoFactory(sqlite_file)

#--------------------------------------------------------------------
class SqliteDaoSession(DaoSession):
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self.db = None

    def get_login_dao(self):
        return SqliteLoginDao(self.db)

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
class SqliteLoginDao:
    def __init__(self, db):
        self.db = db

    def load_logins(self, username, valid = True):
        if valid:
            self.db.execute('select * from logins where username = ? and valid = 1 and expiry_dt > ?' % (
                username, datetime.now()))
        else:
            self.db.execute('select * from logins where username = ?' % (username,))
        
        return [Login(*row) for row in self.db.fetchall()]

    def save_login(self, login):
        self.invalidate_logins(login.username)
        self.db.execute('insert into logins (valid, username, token, expiry_dt) values (?, ?, ?, ?)' % (
            login.valid, login.username, login.token, login.expiry_dt))
    
    def invalidate_logins(self, username):
        self.db.execute('update logins set valid = 0 where username = ?', (username,))
        
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

