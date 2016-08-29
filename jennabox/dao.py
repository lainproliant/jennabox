#--------------------------------------------------------------------
# JennaBox: A lightweight privacy-focused image tagging and
#           sharing website.
#
# Author: Lain Supe (lainproliant)
# Date: Tuesday, August 23rd 2016
#--------------------------------------------------------------------

import cherrypy
import uuid

#--------------------------------------------------------------------
class DaoSessionFactory:
    def get(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class DaoSession:
    def __init__(self, dao_ctor_map):
        self.dao_ctor_map = dao_ctor_map
    
    def get(self, name):
        if not name in self.dao_ctor_map:
            raise ValueError('Dao not provided for resource "%s".' % name)

        return self._provide(dao)
    
    def _provide(self, dao):
        raise NotImplementedError()

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self):
        raise NotImplementedError()

#--------------------------------------------------------------------
class Dao:
    def needs(self, name):
        return False

    def provide(self, name, resource):
        pass

