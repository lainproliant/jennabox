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
    
    def text_field(self, name, label, value = None, placeholder = None):
        return [
            self.label(name, label),
            self.text_input(name, value, placeholder)
        ]

    def password_field(self, name, label, placeholder):
        return [
            self.label(name, label),
            self.password_input(name, placeholder)
        ]
    
    def label(self, name, label):
        return html.label({'for': name, 'class': 'label'})(label)

    def text_input(self, name, value = None, placeholder = None):
        input_element = html.input(type='text', name=name, id=name)({'class': 'text-input'})
        if value is not None:
            input_element(value=value)
        if placeholder is not None:
            input_element(placeholder=placeholder)
        return input_element

    def password_input(self, name, placeholder = None):
        password_element = html.input(type='password', name=name, id=name)({'class': 'password-input'})
        if placeholder is not None:
            password_element(placeholder=placeholder)
        return password_element

    def submit_button(self, label = None):
        button = html.button({'class': 'btn-submit'})(type = 'submit')
        if label is not None:
            button(label)
        return button

    def icon(self, name, classes = []):
        return html.i({'class': ' '.join(['fa', 'fa-' + name] + classes)})

#--------------------------------------------------------------------
markup = MarkupFactory()
