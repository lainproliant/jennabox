#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import logging
import logging.config
import cherrypy
import os

from xeno import *
from .auth import random_password
from .domain import User

#--------------------------------------------------------------------
class ServerModule:
    @provide
    @singleton
    def assets(self):
        return [
            '/static/font-awesome/css/font-awesome.css',
            '/static/css/minimal.css',
            '/static/css/jennabox.css'
        ]

    @provide
    @singleton
    def cherrypy_config(self):
        return {
            '/': {
                'tools.staticdir.root':     os.path.abspath(os.getcwd())
            },
            '/static': {
                'tools.staticdir.on':       True,
                'tools.staticdir.dir':      'static'
            },
            '/images': {
                'tools.staticdir.on':       True,
                'tools.staticdir.dir':      '/opt/jennabox/images'
            }
        }

    @provide
    @singleton
    def log(self):
        logging.config.fileConfig('logging.ini')
        return logging.getLogger()


    @provide
    @singleton
    def admin_user(self, dao_factory, auth, log):
        user_dao = dao_factory.get_user_dao()
        admin = user_dao.get('admin')
        if admin is None:
            log.warn('No admin user exists.  Creating now...')
            password = random_password()
            user = User('admin', rights = ['admin'])
            auth.save_user(user, password)
            log.warn('Admin user created with initial password %s, please change!' % password)
            admin = user_dao.get('admin')
        return admin

