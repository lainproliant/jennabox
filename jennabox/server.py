#!/usr/bin/env python3
#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import json
import os

from datetime import timedelta
from xeno import *

from .auth import AuthModule, LoginFailure
from .config import ServerModule
from .dao import DaoModule
from .framework import server, before, render, require
from .domain import *
from .content import *

#--------------------------------------------------------------------
@server
class JennaBoxServer:
    @before
    def before(self, *args, **kwargs):
        user = self.auth.get_user()
        if (user and
            user.has_attribute(UserAttribute.PASSWORD_RESET_REQUIRED) and
            not cherrypy.request.path_info.startswith('/change_password')):
            raise cherrypy.HTTPRedirect('/change_password')

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
    def upload_post(self, image_file, summary, tags):
        user = self.auth.get_user()
        user_tag = 'user:%s' % user.username
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.save_new_image(image_file, summary, json.loads(tags) + [user_tag])
        raise cherrypy.HTTPRedirect('/view?id=%s' % image.id)

    @cherrypy.expose
    @render
    def view(self, id):
        return ImageViewPage(id)

    @cherrypy.expose
    @require(UserRight.UPLOAD)
    @render
    def edit(self, id):
        return ImageEditPage(id)

    @cherrypy.expose
    @require(UserRight.UPLOAD)
    def edit_post(self, id, summary, tags):
        user = self.auth.get_user()
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.get(id)

        if not image.can_edit(user):
            raise AccessDenied('User "%s" is not allowed to edit image with id "%s".' % (
                user.username, image.id))

        image.tags = set(json.loads(tags))
        image.summary = summary
        image_dao.save_image(image)
        raise cherrypy.HTTPRedirect('/view?id=%s' % image.id)

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
        return ChangePasswordPage()

    @cherrypy.expose
    def change_password_post(self, old_password, new_password_A, new_password_B):
        if new_password_A != new_password_B:
            raise LoginFailure('New password and confirm password do not match.')
        user = self.auth.get_user()
        self.auth.change_password(user, old_password, new_password_A)

    @cherrypy.expose
    @require(UserRight.USER)
    def logout(self):
        login = self.auth.get_login()
        if login is not None:
            self.auth.logout(login)
        else:
            raise cherrypy.HTTPRedirect('/')

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

