#!/usr/bin/env python3
#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import os

from datetime import timedelta
from xeno import *

from .auth import AuthModule, LoginFailure, require
from .config import ServerModule
from .dao import DaoModule
from .framework import BaseServer, render
from .domain import *
from .content import *

#--------------------------------------------------------------------
class JennaBoxServer(BaseServer):
    def __init__(self, injector):
        self.injector = injector

    def before(self, *args, **kwargs):
        user = self.auth.get_user()
        if user.has_attribute(UserAttribute.PASSWORD_RESET_REQUIRED):
            raise cherrypy.HTTPRedirect('/change-password')

    @cherrypy.expose
    @render
    def index(self):
        return ImageSearchPage()

    @cherrypy.expose
    @render
    def search(self, query, page = 0):
        return ImageSearchPage(query, page)

    @cherrypy.expose
    @render
    def login(self):
        return LoginPage()

    @cherrypy.expose
    @require(UserRight.UPLOAD)
    @render
    def upload(self):
        return ImageUploadPage()

    @cherrypy.expose
    @require(UserRight.UPLOAD)
    def upload_post(self, image_file, tags):
        user = self.auth.get_user()
        user_tag = 'user:%s' % user.username
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.save_new_image(image_file, list(tags.split()) + [user_tag])
        raise cherrypy.HTTPRedirect('/view?id=%s' % image.id)

    @cherrypy.expose
    @render
    def view(self, id):
        return ImageViewPage(id)

    @cherrypy.expose
    @require(UserRight.UPLOAD)
    @render
    def edit(self, id):
        return ImageEdit(id)

    @cherrypy.expose
    @require(UserRight.UPLOAD)
    def edit_post(self, id, tags):
        self.auth.require_right(UserRight.UPLOAD)
        pass

    @cherrypy.expose
    @render
    def login_post(self, username, password):
        try:
            self.auth.login(username, password)
        except LoginFailure as e:
            return LoginPage(failed = True)

    @cherrypy.expose
    @require(UserRight.USER)
    @render
    def change_password(self):
        self.auth.require_right(UserRight.USER)
        return ChangePassword()

    @cherrypy.expose
    def change_password_post(self, old_password, new_password_A, new_password_B):
        self.auth.require_right(UserRight.USER)

        if new_password_A != new_password_B:
            raise LoginFailure('New password and confirm password do not match.')
        self.auth.change_password(old_password, new_password_A)

    @cherrypy.expose
    @require(UserRight.USER)
    def logout(self):
        self.auth.logout()

    @cherrypy.expose
    @render
    def images(self, filename):
        pass

#--------------------------------------------------------------------
def main():
    injector = Injector(ServerModule(), DaoModule(),
                        AuthModule(), ContentModule())
    injector.require('admin_user')

    server = injector.create(JennaBoxServer)
    server.start()

#--------------------------------------------------------------------
if __name__ == '__main__':
    main()

