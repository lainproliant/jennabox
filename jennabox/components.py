#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from indent_tools import html
from .renderer import Renderer
from .markup import markup
from .auth import LoginFailure

from xeno import inject

#--------------------------------------------------------------------
class Header(Renderer):
    def __init__(self, user):
        self.user = user

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
            html.div({'class': 'row'})(
                html.div({'class': 'col-6'})(
                    html.a(href='/')(
                        html.h1(
                            markup.icon('camera-retro'),
                            'JennaBox'))),
                html.div({'class': 'col-6'})(html.div({'class': 'float-right login-box'})(login_elements))))

#--------------------------------------------------------------------
class HomePage(Renderer):
    def render(self):
        return html.div({'class': 'intro-box'})(
            html.h1('Welcome'),
            html.h3('JennaBox is a private image hosting and tagging site for you, your friends, and your family.'))

#--------------------------------------------------------------------
class SearchForm(Renderer):
    def render(self):
        return html.form(action='/search', method='get')({'class': 'search-form'})(
            markup.text_input('query', placeholder='Search with tags')({'class': 'col-10'}),
            markup.submit_button()(markup.icon('search'))({'class': 'col-2'}))

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
                markup.submit_button('Login')({'class': 'float-right'})))

        if self.failed:
            container_div(markup.error('Invalid username or password.  Please try again.'))

        return container_div(login_form)

#--------------------------------------------------------------------
class BasicLeftNav(Renderer):
    def render(self):
        return html.div({'class': 'row'})(SearchForm().render())

