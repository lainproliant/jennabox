#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016 #--------------------------------------------------------------------

import logging
import logging.config
import cherrypy
import os

from xeno import *
from .auth import random_password
from .domain import *

#--------------------------------------------------------------------
class ServerModule:
    @provide
    @singleton
    def global_assets(self):
        return [
            '/static/font-awesome/css/font-awesome.css',
            '/static/bootstrap/css/bootstrap.css',
            '/static/bootstrap/css/bootstrap-theme.css',
            '/static/css/jennabox.css',
            '/static/jquery/jquery.js',
            '/static/bootstrap/js/bootstrap.js',
            '/static/js/angular.js',
            '/static/js/jennabox.js'
        ]
    
    @provide
    @singleton
    def image_dir(self):
        return '/opt/jennabox/images'

    @provide
    @singleton
    def image_page_size(self):
        return 12

    @provide
    @singleton
    def cherrypy_config(self, image_dir):
        cherrypy.config.update({
            'server.socket_host':   '0.0.0.0'
        })

        if not os.path.exists(image_dir):
            raise FileNotFoundError('"image_dir" (%s) does not exist.' % image_dir)

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
                'tools.staticdir.dir':      image_dir
            }
        }

    @provide
    @singleton
    def log(self):
        root = logging.getLogger()
        handler = logging.FileHandler('jennabox.log')
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        return root

    @provide
    @singleton
    def admin_user(self, dao_factory, auth, log):
        user_dao = dao_factory.get_user_dao()
        admin = user_dao.get('admin')
        if admin is None:
            log.warn('No admin user exists.  Creating now...')
            password = random_password()
            user = User('admin',
                rights = [UserRight.ADMIN, UserRight.USER],
                attributes = [UserAttribute.PASSWORD_RESET_REQUIRED])
            user.passhash = auth.encrypt_password(password)
            user_dao.put(user)
            log.warn('Admin user created with initial password %s, please change!' % password)
            admin = user_dao.get('admin')
        return admin

