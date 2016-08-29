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
    def __init__(self, username, passhash, rights = None):
        self.username = username
        self.passhash = passhash
        self.rights = rights or []

#--------------------------------------------------------------------
class Login:
    def __init__(self, username, token = None, expiry_dt = None):
        self.username = username
        self.token = token or uuid.uuid4()
        self.expiry_dt = expiry_dt

