#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import uuid
from xenum import xenum

#--------------------------------------------------------------------
@xenum
class UserRight:
    GUEST                       = 0
    ADMIN                       = 1
    USER                        = 2
    UPLOAD                      = 3

    def __init__(self):
        pass

    def __call__(self, f):
        def decorate(server, *args, **kwargs):
            server.auth.require_right(self)
            return f(*args, **kwargs)

#--------------------------------------------------------------------
@xenum
class UserAttribute:
    PASSWORD_RESET_REQUIRED     = 1

#--------------------------------------------------------------------
@xenum
class Action:
    def __init__(self, label, href, rights = None):
        self.label = label
        self.href = href
        self.rights = rights or []

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
    def __init__(self, image_id = None, tags = None, attributes = None):
        self.image_id = (image_id or uuid.uuid4().urn[9:])
        self.tags = (tags or [])
        self.attributes = (attributes or [])

