#!/usr/bin/env python3
import argparse
import collections
import getpass
import json
import logging
import os
import sys
import wand

from jennabox.dao import DaoModule
from jennabox.auth import AuthModule
from jennabox.config import ServerModule
from xeno import *

#--------------------------------------------------------------------
class AdminCommandModule:
    @provide
    @singleton
    def log(self):
        return logging.getLogger()

#--------------------------------------------------------------------
class ClassMap(collections.UserDict):
    def commands(self):
        return sorted(list(self.keys()))

    def __call__(self, name = None):
        def define_impl(f):
            n = name
            if name is None:
                n = f.__name__
            self.data[n] = f
            return f
        return define_impl

cmap = ClassMap()

#--------------------------------------------------------------------
class Config:
    def get_arg_parser(self):
        parser = argparse.ArgumentParser(description = 'Command line interface for managing JennaBox instances.',
                add_help = False)
        parser.add_argument('command', metavar='COMMAND', nargs='?', default=None)
        return parser

    def parse_args(self):
        self.get_arg_parser().parse_known_args(namespace = self)
        return self

#----------------------------------------------------------
@cmap('dump-metadata')
class DumpMetadata(Config):
    def __init__(self, dao_factory):
        self.dao_factory = dao_factory
        self.parse_args()

    def get_arg_parser(self):
        parent = super().get_arg_parser()
        parser = argparse.ArgumentParser(parents = [parent], prog = 'admin.py dump-metadata')
        parser.add_argument('-i', '--image', dest='image_id',
                            metavar='IMAGE_ID', required=True)
        return parser

    def __call__(self):
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.get(self.image_id)
        if image is None:
            raise Exception('No image with id "%s" exists.' % self.image_id)
        image_filename = os.path.join(image_dao.image_dir, image.get_filename())
        metadata_map = {}
        with wand.image.Image(filename = image_filename) as wand_image:
            for key, value in wand_image.metadata.items():
                metadata_map[key] = value

        print(json.dumps(metadata_map, indent=4))

#----------------------------------------------------------
@cmap('reset-password')
class ResetPassword(Config):
    def __init__(self, dao_factory, auth):
        self.dao_factory = dao_factory
        self.auth = auth
        self.parse_args()

    def get_arg_parser(self):
        parent = super().get_arg_parser()
        parser = argparse.ArgumentParser(parents = [parent], prog = 'admin.py reset-password')
        parser.add_argument('-u', '--username', metavar='USERNAME', required=True)
        return parser

    def __call__(self):
        user_dao = self.dao_factory.get_user_dao()
        user = user_dao.get(self.username)
        if user is None:
            raise Exception('Unknown user "%s"' % self.username)
       
        passwordA = getpass.getpass(prompt = 'Password: ')
        passwordB = getpass.getpass(prompt = 'Confirm password: ')

        if passwordA != passwordB:
            raise Exception('Passwords do not match.')

        user.passhash = self.auth.encrypt_password(passwordA)
        user_dao.put(user)

        print('Password changed successfully.')

#----------------------------------------------------------
def main():
    try:
        config = Config().parse_args()
        if config.command is None:
            raise Exception('Command is required, known commands: %s' % ', '.join(cmap.commands()))

        if config.command not in cmap:
            raise Exception('Unknown command, known commands: %s' % ', '.join(cmap.commands()))

        injector = Injector(AdminCommandModule(), DaoModule(),
                            AuthModule(), ServerModule())
        injector.create(cmap[config.command])()

    except Exception as e:
        print(str(e))
        sys.exit(1)

#----------------------------------------------------------
if __name__ == '__main__':
    main()
