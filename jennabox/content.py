#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

from .auth import LoginFailure
from .domain import *
from .framework import Renderer, HTML, AssetList
from .markup import markup

from urllib.parse import urlencode
from indenti import html
from xeno import inject, provide

#--------------------------------------------------------------------
class Page(Renderer):
    def render(self):
        return html.html({'ng-app': 'JennaBox'}).doctype('html')(
            html.head(
                html.title(self.title())),
                AssetList().assets(self.assets()).render(),
                self.body())

    def body(self):
        content = self.content()
        nav = self.nav.render()
        return [
            self.header.render(),
            html.div({'class': 'container-fluid'})(
                html.div({'class': 'row'})(
                    html.div({'class': 'col-md-2'})(nav),
                    html.div({'class': 'col-md-10'})(content)))
        ]
    
    def title(self):
        return "Jennabox"

    def assets(self):
        return self.global_assets

    def content(self):
        raise NotImplementedError()

    @inject
    def inject_deps(self, injector, header, nav, global_assets):
        self.global_assets = global_assets
        self.header = header
        self.nav = nav

#--------------------------------------------------------------------
class Header(Renderer):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.user = auth.get_user()

    def render(self):
        login_elements = []

        if self.user.is_guest():
            login_elements = [
                html.li(html.p({'class': 'navbar-text'})('Not logged in')),
                html.li(html.a('Login', markup.icon('sign-in'), {'href': '/login'}))
            ]
        else:
            login_elements = [
                html.li(html.p({'class': 'navbar-text'})('Logged in as %s' % self.user.username)),
                html.li(html.a('Logout', markup.icon('sign-out'), {'href': '/logout'}))
            ]

        return html.nav({'class': 'navbar navbar-inverse navbar-fixed-top'})(
            html.div({'class': 'container-fluid'})(
                html.div({'class': 'navbar-header'})(
                    html.button({'type': 'button', 'class': 'navbar-toggle collapsed', 'data-toggle': 'collapse',
                                 'data-target': '#navbar', 'aria-expanded': 'false', 'aria-controls': 'navbar'})(
                        html.span({'class': 'sr-only'})('Toggle navigation'),
                        html.span({'class': 'icon-bar'}),
                        html.span({'class': 'icon-bar'}),
                        html.span({'class': 'icon-bar'})),
                    html.a({'class': 'navbar-brand', 'href': '/'})(markup.icon('camera-retro'), "Jenna's Photo Box")),
                html.div({'id': 'navbar', 'class': 'navbar-collapse collapse'})(
                    html.ul({'class': 'nav navbar-nav navbar-right'})(
                        login_elements,
                        [html.li(html.a(href = action().href)(
                            action().label,
                            markup.icon(action().icon))) for action in Action.values() if action().is_available(self.user)]),
                    html.form({'class': 'navbar-form navbar-right', 'action': '/search', 'method': 'get'})(
                        html.input({'type': 'text', 'name': 'query', 'class': 'form-control', 'placeholder': 'Search with tags'})))))

#--------------------------------------------------------------------
class LeftNav:
    def __init__(self, auth):
        self.auth = auth
        self.tags = []
        self.image = None

    def set_tags_from_images(self, images):
        tags = set()

        for image in images:
            for tag in image.tags:
                tags.add(tag)

        self.tags = sorted(list(tags))

    def set_image(self, image):
        self.image = image
        self.set_tags_from_images([image])

    def render(self):
        container = html.div({
            'class': 'left-nav',
            'ng-controller': 'ImageTagController as ctrl'})

        container(html.input({
            'type':         'hidden',
            'value':        ' '.join(self.tags)}))

        row = html.div({'class': 'row image-controls'})
        user = self.auth.get_user()
        if self.image and user:
            user_tag = 'user:%s' % user.username
            if self.image.can_edit(user):
                row(markup.button('Edit', '/edit?' + urlencode({'id': self.image.id}),
                    lefticon = 'pencil-square-o'))
                container(row)
        
        row = html.div({'class': 'row'})
        container(row)
        
        row(html.a({'ng-repeat': 'tag in ctrl.tags.split(" ")', 'ng-href': '/search?query={{tag}}'})(
            html.span({'ng-style': 'ctrl.getTagStyles(tag)', 'class': 'badge'}, '{{tag}}')))

        return container

#--------------------------------------------------------------------
class ImageSearchPage(Page):
    def __init__(self, query = '', page = 1):
        super().__init__()
        self.tags = []
        self.ntags = []
        self.page = int(page)
        self.query = query

        for tag in query.split():
            if tag.startswith('-'):
                self.ntags.append(tag[1:])
            else:
                self.tags.append(tag)

    def content(self):
        results = []
        image_dao = self.dao_factory.get_image_dao()

        # Non logged in users must only see images with 'public'
        if not self.user.has_right(UserRight.USER):
            self.tags.append('public')
            self.ntags = list(filter(lambda x: x != 'public', self.ntags))

        images, count = image_dao.find(self.tags, self.ntags,
                                       self.image_page_size, self.image_page_size * (self.page - 1))

        self.nav.set_tags_from_images(images)

        row = html.div({'class': 'row'})
        ul = html.ul({'class': 'pagination'})
        row(ul)
        
        page_count = 1 + int((count - 1) / (self.image_page_size or 1))
        if page_count > 1:
            for x in range(0, page_count):
                page_num = x + 1
                button = markup.button('%d' % page_num, '/search?' + urlencode({
                        'query':    self.query,
                        'page':     page_num}))
                ul(button)

                if self.page == page_num:
                    button({'class': 'btn-current'})
                else:
                    button({'class': 'btn-inverse'})

        results.append(row)

        row = html.div({'class': 'row'})
        for image in images:
            row(html.div({'class': 'col-md-3 image-result'})(
                html.a({'href': '/view?id=%s' % image.id})(
                    html.img({'src': '/images/mini/' + image.get_filename(), 'class': 'mini-image'}))))
        results.append(row)

        return results

    @inject
    def inject_deps(self, auth, dao_factory, image_page_size):
        self.user = auth.get_user()
        self.auth = auth
        self.dao_factory = dao_factory
        self.image_page_size = image_page_size

#--------------------------------------------------------------------
class ImageViewPage(Page):
    def __init__(self, id):
        super().__init__()
        self.id = id

    def content(self):
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.get(self.id)
        if not image:
            raise cherrypy.NotFound()

        self.nav.set_image(image)

        return html.a({'href': '/images/' + image.get_filename()})(
            html.img({'src': '/images/' + image.get_filename(), 'class': 'image-view'}))

    @inject
    def inject_deps(self, dao_factory):
        self.dao_factory = dao_factory

#--------------------------------------------------------------------
class EmptyPage(Page):
    def content(self):
        return html.h1("Nothing to see here!")

#--------------------------------------------------------------------
class LoginPage(Page):
    def __init__(self, failed = False):
        super().__init__()
        self.failed = failed

    def content(self):
        elements = []

        if self.failed:
            elements.append(markup.error('Invalid user name or password.  Please try again.'))

        elements.append(html.form({'action': '/login_post', 'method': 'post', 'class': 'form-signin'})(
            html.h2('Log In', {'class': 'form-signin-heading'}),
            markup.text_input('username', placeholder = 'Username')({'class': 'form-control'}),
            markup.password_input('password', placeholder = 'Password')({'class': 'form-control'}),
            markup.submit_button('Log In')({'class': 'btn btn-lg btn-inverse btn-block'})))

        return elements

#--------------------------------------------------------------------
class ImageUploadPage(Page):
    def content(self):
        form = html.form({'class': 'form-horizontal'}, action='/upload_post', method='post', enctype='multipart/form-data')(
            html.div({'class': 'form-group'})(
                html.input(id='image_selector', type = 'file', name = 'image_file')),
            html.div({'class': 'form-group'})(
                html.textarea(name = 'tags', placeholder = 'Enter space-delimited tags')),
            html.div({'class': 'form-group'})(
                html.img(id = 'upload-preview', src='/static/images/placeholder.png')),
            html.div({'class': 'form-group'})(
                markup.submit_button('Upload Image')(disabled = None)))

        return [markup.js('/static/js/image_upload.js'), form]

#--------------------------------------------------------------------
class ImageEdit(Page):
    def __init__(self, id):
        super().__init__()
        self.id = id

    def content(self):
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.get(self.id)

        if not image.can_edit(user, self.auth):
            raise AccessDenied('User "%s" is not allowed to edit image with id "%s".' % (
                user.username, image.id))

        form = html.form({'class': 'form-horizontal'}, action='/edit_post', method='post')(
            html.div({'class': 'form-group'})(
                html.textarea(name = 'tags', placeholder = 'Enter space-delimited tags')(' '.join(image.tags))),
            html.div({'class': 'form-group'})(
                html.img(id = 'upload-preview', src='/images/' + image.get_filename())),
            html.div({'class': 'form-group'})(
                markup.submit_button('Edit Image')))

        return form

    @inject
    def inject_deps(self, auth, dao_factory):
        self.dao_factory = dao_factory
        self.auth = auth

#--------------------------------------------------------------------
class ChangePasswordPage(Page):
    def __init__(self, failed = False):
        super().__init__()
        self.failed = failed

    def content(self):
        container_div = html.div({'ng-controller': 'ChangePasswordController as ctrl'})
        form = html.form({'name': 'ctrl.form', 'action': '/change_password_post',
            'method': 'post', 'class': 'form-signin'})(
            html.h2('Change Password', {'class': 'form-signin-heading'}),
            markup.password_input('old_password', placeholder = 'your old password')(
                {'ng-model': 'ctrl.oldPassword', 'class': 'form-control'}),
            markup.password_input('new_password_A', placeholder = 'your new password')(
                {'ng-model': 'ctrl.newPasswordA', 'class': 'form-control'}),
            markup.password_input('new_password_B', placeholder = 'confirm new password')(
                {'ng-model': 'ctrl.newPasswordB', 'class': 'form-control'}),
            markup.submit_button('Change Password')(
                {'ng-disabled': '(!ctrl.newPasswordA.trim()) || (ctrl.newPasswordA != ctrl.newPasswordB)',
                 'class': 'btn btn-lg btn-inverse btn-block'}))

        if self.failed:
            container_div(markup.error('Old password is incorrect, please try again.'))

        return container_div(form)

#--------------------------------------------------------------------
class ContentModule:
    @provide
    def nav(self, injector):
        return injector.create(LeftNav)

    @provide
    def header(self, injector):
        return injector.create(Header)

