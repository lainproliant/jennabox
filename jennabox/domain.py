#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import uuid
from datetime import datetime
from xenum import xenum, sref, ctor

from .markup import *

#--------------------------------------------------------------------
@xenum
class UserRight:
    GUEST   = sref()
    ADMIN   = sref()
    USER    = sref()
    UPLOAD  = sref()

    def __init__(self, enum):
        self.enum = enum

    def __call__(self, f):
        def decorate(server, *args, **kwargs):
            server.auth.require_right(self.enum)
            return f(*args, **kwargs)

#--------------------------------------------------------------------
@xenum
class UserAttribute:
    PASSWORD_RESET_REQUIRED = 1

#--------------------------------------------------------------------
@xenum
class Action:
    UPLOAD  = ctor(['Upload', markup.icon('upload')], '/upload_page', [UserRight.UPLOAD])
    CPANEL  = ctor(['Control Panel', markup.icon('cog')], '/control_panel', [UserRight.ADMIN])

    def __init__(self, label, href, rights = None):
        self.label = label
        self.href = href
        self.rights = rights or []
    
    def is_available(self, auth):
        for right in self.rights:
            if not auth.has_right(right):
                return False
        return True

    def __call__(self, f):
        def decorate(server, *args, **kwargs):
            for right in self.rights:
                server.auth.require_right(right)
            return f(*args, **kwargs)

#--------------------------------------------------------------------
class User:
    def __init__(self, username, passhash = None, rights = None,
                 attributes = None):
        self.username = username
        self.passhash = passhash
        self.rights = set(rights or set())
        self.attributes = set(attributes or set())

    def add_attribute(self, attr):
        self.attributes.add(attr)

    def remove_attribute(self, attr):
        if attr in self.attributes:
            self.attributes.remove(attr)

    def add_right(self, right):
        self.rights.add(right)

    def remove_right(self, right):
        if right in self.rights:
            self.rights.remove(right)

#--------------------------------------------------------------------
class Login:
    def __init__(self, username, expiry_dt, token = None):
        self.username = username
        self.expiry_dt = expiry_dt
        self.token = token or uuid.uuid4().urn[9:]

#--------------------------------------------------------------------
class Image:
    MIME_EXT_MAP = {
        'image/jpeg':   '.jpg',
        'image/png':    '.png',
        'image/gif':    '.gif',
        'video/mp4':    '.gifv'
    }

    THUMB_RESIZE_TRANSFORM = '300x400>'

    def __init__(self, id = None, mime_type = None, timestamp = None, tags = None, attributes = None):
        if not mime_type in Image.MIME_EXT_MAP:
            raise ValueError('Invalid Image mime_type: %s' % mime_type)

        self.id = (id or uuid.uuid4().urn[9:])
        self.mime_type = mime_type
        self.tags = set(tags or [])
        self.attributes = set(attributes or [])
        self.timestamp = timestamp or datetime.now()

    def get_filename(self):
        return self.id + Image.MIME_EXT_MAP[self.mime_type]

