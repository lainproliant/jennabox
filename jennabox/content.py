#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import urllib

from .auth import LoginFailure
from .domain import *
from .framework import Renderer, HTML, AssetList
from .markup import markup

from indenti import html
from xeno import inject, provide

#--------------------------------------------------------------------
class ContentModule:
    @provide
    def header(self, auth):
        return Header(auth) 

    @provide
    def nav(self, injector):
        return injector.create(LeftNav)

    @provide
    def assets(self, global_assets):
        return AssetList().assets(global_assets)

#--------------------------------------------------------------------
class Page(Renderer):
    def __init__(self, content, title = "JennaBox <3"):
        super().__init__()
        self._content = content
        self._title = title
    
    def render(self):
        return html.html().doctype('html')(
            html.head(
                html.title(self._title)),
                self.assets.render(),
                self.body())

    def body(self):
        return [
            self.header.render(),
            html.div({'class': 'container'})(
                self.header.render(),
                html.div({'class': 'row'})(
                    html.div(id = 'nav')({'class': 'col-2 nav-container'})(self.nav.render()),
                    html.div(id = 'content')({'class': 'col-10 content-container'})(self.content.render())))
        ]

    @inject
    def inject_deps(self, injector, assets, nav, header):
        self.assets = assets
        self.nav = nav
        self.header = header
        injector.inject(self._content)

#--------------------------------------------------------------------
class Header(Renderer):
    def __init__(self, auth):
        self.auth = auth
        self.user = auth.get_current_user()

    def render(self):
        login_elements = []

        if self.user is None:
            login_elements = [
                html.span('Not logged in'),
                markup.button('Login', '/login_page', righticon = 'sign-in')
            ]
        else:
            login_elements = [
                html.span('Logged in as %s' % self.user.username),
                markup.button('Logout', '/logout', righticon = 'sign-out')
            ]

        return html.header(
            html.nav({'class': 'navbar navbar-inverse navbar-fixed-top'})(
                html.button({'type': 'button', 'class': 'navbar-toggle collapsed', 'data-toggle': 'collapse',
                             'data-target': 'navbar', 'aria-expanded': 'false', 'aria-controls': 'navbar'}),
                html.a({'class': 'navbar-brand', 'href': '/'})(markup.icon('camera-retro'), 'JennaBox'),
            html.div({'id': 'navbar', 'class': 'navbar-collapse collapse', 'aria-expanded': 'false', 'style': 'height: 1px;'})(
                html.ul({'class': 'nav navbar-nav navbar-right'})(
                    [html.li(html.a(href = action.href)(action.label)) for action in self.auth.get_actions()]),
                html.form({'class': 'navbar-form navbar-right'})(
                    markup.text_input('query', placeholder='Search with tags')))))

#--------------------------------------------------------------------
class ImageSearch(Renderer):
    def __init__(self, query = '', page = 0):
        self.tags = []
        self.ntags = []
        self.page = page
        self.query = query
        
        for tag in query.split():
            if tag.startswith('-'):
                self.ntags.append(tag[1:])
            else:
                self.tags.append(tag)
    
    def render(self):
        image_dao = self.dao_factory.get_image_dao()
        
        # Non logged in users must only see images with 'public'
        if not self.auth.has_right(UserRight.USER):
            self.tags.append('public')
            self.ntags = list(filter(lambda x: x != 'public', self.ntags))

        images, count = image_dao.find(self.tags, self.ntags,
                                       self.image_page_size, self.image_page_size * self.page)

        image_rows = []
        row = None
        for x in range(len(images)):
            image = images[x]
            if row is None or x % 3 == 0:
                row = html.div({'class': 'row'})
                image_rows.append(row)

            row(
                html.div({'class': 'col-3 mini-image'})(
                    html.a(href = '/view?id=%s' % image.id)(
                        html.img(src = '/images/mini/' + image.get_filename()))))
        
        row = html.div({'class': 'row'})
        image_rows.append(row)
        for x in range(int(count / (self.image_page_size or 1))):
            row(markup.button('%d' % x, '/search?' + urllib.urlencode({
                'query':    self.query,
                'page':     self.page})))
        
        return image_rows
        
    @inject
    def inject_deps(self, auth, dao_factory, image_page_size):
        self.user = auth.get_current_user()
        self.auth = auth
        self.dao_factory = dao_factory
        self.image_page_size = image_page_size

#--------------------------------------------------------------------
class ImageView(Renderer):
    def __init__(self, id):
        self.id = id

    def render(self):
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.get(self.id)
        if not image:
            raise cherrypy.NotFound()

        return html.img(src = '/images/' + image.get_filename())

    @inject
    def inject_deps(self, dao_factory):
        self.dao_factory = dao_factory

#--------------------------------------------------------------------
class EmptyPage(Renderer):
    def render(self):
        return html.h1("Nothing to see here!")

#--------------------------------------------------------------------
class SearchForm(Renderer):
    def render(self):
        return html.form(action='/search', method='get')({'class': 'search-form'})(
            markup.text_input('query', placeholder='Search with tags'),
            markup.submit_button()(markup.icon('search'))({'class': 'search-button'}))

#--------------------------------------------------------------------
class LoginForm(Renderer):
    def __init__(self, failed = False):
        self.failed = failed

    def render(self):
        container_div = html.div()
        login_form = html.form(action='/login', method='post')({'class': 'login-form col-4'})(
            html.div({'class': 'row'})(
                markup.text_field('username', 'Username:', placeholder = 'your username')),
            html.div({'class': 'row'})(
                markup.password_field('password', 'Password:', placeholder = 'your password')),
            html.div({'class': 'row'})(
                markup.submit_button('Login')))

        if self.failed:
            container_div(markup.error('Invalid username or password.  Please try again.'))

        return container_div(login_form)

#--------------------------------------------------------------------
class ImageUploadForm(Renderer):
    def render(self):
        form = html.form(action='/upload', method='post', enctype='multipart/form-data')(
            html.div({'class': 'row'})(
                html.input(id='image_selector', type = 'file', name = 'image_file')),
            html.div({'class': 'row'})(
                markup.text_field('tags', 'Tags:', placeholder = 'Enter space-delimited tags')),
            html.div({'class': 'row'})(
                html.img(id = 'upload-preview', src='/static/images/placeholder.png')),
            html.div({'class': 'row'})(
                markup.submit_button('Upload Image')(disabled = None)))

        return [markup.js('/static/js/image_upload.js'), form]

#--------------------------------------------------------------------
class ChangePasswordForm:
    def __init__(self, failed = False):
        self.failed = failed

    def render(self):
        container_div = html.div()
        login_form = html.form(action='/change_password', method='post')({'class': 'login-form col-4'})(
            html.div({'class': 'row'})(
                markup.password_field('old_password', 'Old Password:', placeholder = 'your old password')),
            html.div({'class': 'row'})(
                markup.password_field('new_password_A', 'New Password:', placeholder = 'your new password')),
            html.div({'class': 'row'})(
                markup.password_field('new_password_B', 'Confirm:', placeholder = 'your new password')),
            html.div({'class': 'row'})(
                markup.submit_button('Change Password')))

        if self.failed:
            container_div(markup.error('Old password is incorrect, please try again.'))

        return container_div(login_form)

#--------------------------------------------------------------------
class LeftNav(Renderer):
    def __init__(self, auth):
        self.auth = auth

    def render(self):
        elements = [html.div({'class': 'row'})(SearchForm().render())]
        if self.auth.has_right(UserRight.UPLOAD):
            elements.append(html.div({'class': 'row'})(
                markup.button('Upload', '/upload_page', 'upload')))
        return elements

