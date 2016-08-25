#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from indent_tools import html

#--------------------------------------------------------------------
class MarkupFactory:
    def js(self, src):
        return html.script(type='text/javascript', src=src)

    def css(self, href):
        return html.link(rel='stylesheet', type='text/css', href=href)

    def link(self, title, href):
        return html.a(title, href=href)

    def text_input(self, name, value = None, placeholder = None):
        input_element = html.input(type='text', name=name)
        if value is not None:
            input_element = input_element(value=value)
        if placeholder is not None:
            input_element = input_element(placeholder=placeholder)
        return input_element

    def submit_button(self, label = 'Submit'):
        return html.input(type='submit', value=label)

#--------------------------------------------------------------------
markup = MarkupFactory()
