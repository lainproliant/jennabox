#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from indent_tools import html
from .renderer import Renderer, PageRenderer
from .markup import markup
from .auth import LoginFailure
from .domain import *

from xeno import inject, provide

#--------------------------------------------------------------------
class ContentModule:
    @provide
    def header(self, auth):
        return Header(auth) 

    @provide
    def nav(self, injector):
        return injector.create(LeftNav)

#--------------------------------------------------------------------
class Page(PageRenderer):
    def __init__(self, content):
        super().__init__()
        self.content = content

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
    def set_header(self, header):
        self.header = header
    
    @inject
    def set_nav(self, nav):
        self.nav = nav
    
    @inject
    def inject_content_deps(self, injector):
        injector.inject(self.content)

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
    def __init__(self, query = ''):
        self.query = query

    def render(self):
        if not self.user:
            return self.render_guest_search()
        else:
            return self.render_user_search()

    def render_guest_search(self):
        return EmptyPage().render()

    def render_user_search(self):
        return EmptyPage().render()

    @inject
    def inject_deps(self, auth, dao_factory):
        self.user = auth.get_current_user()
        self.auth = auth
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
        return html.form(action='/upload', method='post', enctype='multipart/form-data')(
            html.div({'class': 'row'})(
                html.input(type = 'file', name = 'file')),
            html.div({'class': 'row'})(
                markup.text_field('tags', 'Tags:', placeholder = 'Enter space-delimited tags')))

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

