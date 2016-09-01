#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import uuid

#--------------------------------------------------------------------
class User:
    def __init__(self, username, passhash = None, rights = None,
                 attributes = None)
        self.username = username
        self.passhash = passhash
        self.rights = set(rights or set())
        self.attributes = set(attributes or set())

#--------------------------------------------------------------------
class Login:
    def __init__(self, username, expiry_dt, token = None):
        self.username = username
        self.expiry_dt = expiry_dt
        self.token = token or uuid.uuid4().urn[9:]

