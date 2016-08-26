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

#--------------------------------------------------------------------
class Header(Renderer):
    def render(self):
        return html.header(html.h1(
            markup.icon('camera-retro'),
            'JennaBox'))

#--------------------------------------------------------------------
class SearchForm(Renderer):
    def render(self):
        return html.form(action='/search', method='get')({'class': 'search-form'})(
            markup.text_input('query', placeholder='Search with tags')({'class': 'col-10'}),
            markup.submit_button()(markup.icon('search'))({'class': 'col-2'}))

#--------------------------------------------------------------------
class LoginForm(Renderer):
    def render(self):
        return html.form(action='/login', method='post')({'class': 'login-form col-4'})(
            html.div({'class': 'row'})(
                markup.text_field('username', 'Username:', placeholder = 'your username')),
            html.div({'class': 'row'})(
                markup.password_field('username', 'Password:', placeholder = 'your password')),
            html.div({'class': 'row'})(
                markup.submit_button('Login')({'class': 'float-right'})))
        
#--------------------------------------------------------------------
class BasicLeftNav(Renderer):
    def render(self):
        return html.div({'class': 'row'})(SearchForm().render())

