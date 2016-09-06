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

from .auth import AuthModule, LoginFailure
from .config import ServerModule
from .dao import DaoModule
from .framework import BaseServer, page
from .domain import *
from .content import *

#--------------------------------------------------------------------
class JennaBoxServer(BaseServer):
    @page
    def index(self):
        return ImageSearch()

    @page
    def search(self, query, page = 0):
        return ImageSearch(query, page)

    @page
    def login_page(self):
        return LoginPage()

    @page
    def upload_page(self):
        self.auth.require_right(UserRight.UPLOAD)
        return ImageUploadPage()

    @page
    def upload(self, image_file, tags):
        self.auth.require_right(UserRight.UPLOAD)
        user = self.auth.get_current_user()
        user_tag = 'user:%s' % user.username
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.save_new_image(image_file, list(tags.split()) + [user_tag])
        raise cherrypy.HTTPRedirect('/view?id=%s' % image.id)
    
    @page
    def view(self, id):
        return ImageView(id)

    @page
    def login(self, username, password):
        try:
            self.auth.login(username, password)
        except LoginFailure as e:
            return LoginPage(failed = True)
    @page
    @UserRight.USER()
    def change_password_page(self):
        self.auth.require_right(UserRight.USER)
        return ChangePasswordPage()

    @page
    @UserRight.USER()
    def change_password(self, old_password, new_password_A, new_password_B):
        # TODO: Make this fail more gracefully, like on the front end maybe.
        self.auth.require_right(UserRight.USER)
        if new_password_A != new_password_B:
            raise LoginFailure('New password and confirm password do not match.')
        self.auth.change_password(old_password, new_password_A)

    @page
    def logout(self):
        self.auth.logout()

    @inject
    def require_admin_user(self, admin_user):
        pass

    def before(self):
        user = self.auth.get_current_user()
        if (user is not None and
                not cherrypy.request.path_info.startswith('/change_password') and
                UserAttribute.PASSWORD_RESET_REQUIRED in user.attributes):
            raise cherrypy.HTTPRedirect('/change_password_page')

#--------------------------------------------------------------------
def main():
    injector = Injector(ServerModule(), DaoModule(),
                        AuthModule(), ContentModule())
    server = injector.create(JennaBoxServer)
    server.start()

#--------------------------------------------------------------------
if __name__ == '__main__':
    main()

