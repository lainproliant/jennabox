#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import collections
import os
import sqlite3

from datetime import datetime
from xeno import *

from .dao import *
from .domain import *

#--------------------------------------------------------------------
class DaoModule:
    @provide
    @singleton
    def db_file(self):
        return 'jennabox.sqlite3'

    @provide
    @singleton
    def ddl_file(self):
        return 'jennabox-ddl.sql'

    @provide
    def db_conn(self, log, db_file, ddl_file):
        if not hasattr(cherrypy.thread_data, 'db_conn'):
            if not os.path.exists(db_file):
                log.warn('sqlite database does not exist.  Creating...')
                with sqlite3.connect(db_file) as db:
                    with open(ddl_file, 'rt') as infile:
                        db.executescript(infile.read())
                log.warn('sqlite database created successfully.')
            cherrypy.thread_data.db_conn = sqlite3.connect(db_file)
        return cherrypy.thread_data.db_conn

    @provide
    @singleton
    def dao_factory(self, injector):
        return SqliteDaoFactory(injector)

#--------------------------------------------------------------------
class SqliteDaoFactory:
    def __init__(self, injector):
        self.injector = injector
        self.login_dao = InMemoryLoginDao()

    def get_user_dao(self):
        return self.injector.create(SqliteUserDao)

    def get_login_dao(self):
        return self.login_dao

#--------------------------------------------------------------------
class InMemoryLoginDao:
    def __init__(self):
        self.cache = {}

    def get(self, token):
        if token in self.cache:
            return self.cache.get(token)
        else:
            return None

    def put(self, login):
        self.cache[login.token] = login

    def drop(self, token):
        del self.cache[token]

    def clear_expired_logins(self):
        now = datetime.now()
        for token, login in self.cache.items():
            if now > login.expiry_dt:
                self.drop(token)

#--------------------------------------------------------------------
class SqliteUserDao:
    def __init__(self, db_conn):
        self.db = db_conn

    def get(self, username):
        users = self.get_users([username])
        if users:
            return list(users)[0]
        else:
            return None

    def get_users(self, usernames):
        c = self.db.cursor()
        c.execute('select * from users where username in (%s)' % (','.join('?' * len(usernames))), usernames)
        user_map = collections.OrderedDict()
        for row in c.fetchall():
            user = User(*row)
            user_map[user.username] = user

        c.execute('select * from user_rights where username in (%s)' % (','.join('?' * len(usernames))), usernames)
        for row in c.fetchall():
            username, right = row
            if username in user_map:
                user_map[username].rights.add(UserRight.by_name(right))

        c.execute('select * from user_attributes where username in (%s)' % (','.join('?' * len(usernames))), usernames)
        for row in c.fetchall():
            username, attribute = row
            if username in user_map:
                user_map[username].attributes.add(UserAttribute.by_name(attribute))

        return user_map.values()

    def put(self, user):
        c = self.db.cursor()
        c.execute('insert or replace into users (username, passhash) values (?, ?)', (user.username, user.passhash))
        c.execute('delete from user_rights where username = ?', (user.username,))
        c.execute('delete from user_attributes where username = ?', (user.username,))
        for right in user.rights:
            c.execute('insert into user_rights (username, app_right) values (?, ?)', (user.username, str(right)))
        for attribute in user.attributes:
            c.execute('insert into user_attributes (username, attribute) values (?, ?)', (user.username, str(attribute)))
        self.db.commit()

