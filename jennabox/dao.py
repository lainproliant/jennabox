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
import wand.image

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

    def get_image_dao(self):
        return self.injector.create(SqliteImageDao)

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
            return users[0]
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

        return list(user_map.values())

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

#--------------------------------------------------------------------
class SqliteImageDao:
    def __init__(self, db_conn, image_dir, image_page_size):
        self.db = db_conn
        self.image_dir = image_dir
        self.image_page_size = image_page_size

        mini_dir = os.path.join(self.image_dir, 'mini')
        if not os.path.exists(mini_dir):
            os.makedirs(mini_dir)

    def save_new_image(self, image_file, summary, tags):
        image = Image(mime_type = str(image_file.content_type), summary = summary, tags = tags)
        image_filename = os.path.join(self.image_dir, image.get_filename())
        mini_filename = os.path.join(self.image_dir, 'mini', image.get_filename())

        with open(image_filename, 'wb') as outfile:
            while True:
                data = image_file.file.read(8192)
                if not data:
                    break
                outfile.write(data)

        # TODO: this probably can't actually handle gifv
        with wand.image.Image(filename = image_filename) as wand_image:
            wand_image.transform(resize = Image.THUMB_RESIZE_TRANSFORM)
            wand_image.save(filename = mini_filename)

        self.save_image(image)
        return image

    def save_image(self, image):
        c = self.db.cursor()
        c.execute('insert or replace into images(id, mime_type, summary, ts) values(?, ?, ?, ?)', (image.id, image.mime_type, image.summary, image.timestamp))
        c.execute('delete from image_tags where id = ?', (image.id,))
        for tag in image.tags:
            c.execute('insert into image_tags (id, tag) values(?, ?)', (image.id, tag))
        self.db.commit()

    def find(self, tags, ntags, limit = None, offset = 0):
        if limit is None:
            limit = self.image_page_size

        c = self.db.cursor()
        c.execute(self._build_select_count_query(tags, ntags), tags + ntags)
        count = c.fetchone()[0]
        c.execute(self._build_select_query(tags, ntags, limit, offset), tags + ntags)
        return self.get_images([x[0] for x in c.fetchall()]), count

    def get(self, image_id):
       images = self.get_images([image_id])
       if images:
           return images[0]
       else:
           return None

    def get_images(self, image_ids):
        if not image_ids:
            return []

        c = self.db.cursor()
        c.execute('select * from images where id in (%s)' % (','.join('?' * len(image_ids))), image_ids)
        image_map = collections.OrderedDict()
        for row in c.fetchall():
            image = Image(*row)
            image_map[image.id] = image

        c.execute('select * from image_tags where id in (%s)' % (','.join('?' * len(image_ids))), image_ids)

        for row in c.fetchall():
            id, tag = row
            if id in image_map:
                image_map[id].tags.add(tag)

        return list(image_map.values())

    def _build_select_count_query(self, tags, ntags):
        query = 'select count(*) from images where {tag_queries} and {ntag_queries}'
        return query.format(
            tag_queries = self._build_tag_subquery(tags),
            ntag_queries = self._build_tag_subquery(ntags, eq = False))

    def _build_select_query(self, tags, ntags, limit, offset):
        query = 'select id from images where {tag_queries} and {ntag_queries} order by datetime(images.ts) desc limit %d offset %d' % (limit, offset)
        return query.format(
            tag_queries = self._build_tag_subquery(tags),
            ntag_queries = self._build_tag_subquery(ntags, eq = False))

    def _build_tag_subquery(self, tags, eq = True):
        subqueries = []
        if not tags:
            return '1'

        subquery = None
        if eq:
            subquery = 'id in ({subselect})'
        else:
            subquery = 'id not in ({subselect})'

        for tag in tags:
            subqueries.append(subquery.format(
                subselect = 'select id from image_tags where tag collate nocase = ?'))

        return ' and '.join(subqueries)

