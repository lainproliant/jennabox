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
from jennabox.auth import AuthModule, random_password, input_password
from jennabox.config import ServerModule
from jennabox.domain import *
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
@cmap('backfill-metadata')
class BackfillMetadata(Config):
    BATCH_SIZE = 5

    def __init__(self, dao_factory):
        self.dao_factory = dao_factory
        self.parse_args()

    def __call__(self):
        image_dao = self.dao_factory.get_image_dao()
        images, total = image_dao.find([], [], limit = BackfillMetadata.BATCH_SIZE)
        offset = 0

        print('==> Scanning %d total images for metadata backfill.', total)
        while offset < total:
            for image in images:
                print('-> Scanning %s... [%s]' % (image.id, ', '.join(sorted(list(image.tags)))))
                original_tags = set(image.tags)
                image.populate_from_metadata(image_dao.get_metadata(image))
                difference_set = image.tags - original_tags
                if difference_set:
                    print('\tAdding tags [%s]' % (', '.join(sorted(list(difference_set)))))
                    image_dao.save_image(image)

            print('==> Processed %d/%d images (%%%d)' % (
                offset + len(images), total,
                int(100 * float(offset + len(images)) / float(total))))

            offset += len(images)
            images, total = image_dao.find([], [], limit = BackfillMetadata.BATCH_SIZE, offset = offset)

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
        metadata_map = image_dao.get_metadata(image)
        print(json.dumps(metadata_map, indent=4))

#----------------------------------------------------------
@cmap('delete-image')
class DeleteImage(Config):
    def __init__(self, dao_factory):
        self.dao_factory = dao_factory
        self.parse_args()

    def get_arg_parser(self):
        parent = super().get_arg_parser()
        parser = argparse.ArgumentParser(parents = [parent], prog = 'admin.py delete-image')
        parser.add_argument('-i', '--image', dest='image_id',
                            metavar='IMAGE_ID', required=True)
        return parser

    def __call__(self):
        image_dao = self.dao_factory.get_image_dao()
        image = image_dao.get(self.image_id)
        image_dao.delete_image(image)
        print('Image %s deleted.' % self.image_id)

#----------------------------------------------------------
@cmap('add-user')
class AddUser(Config):
    def __init__(self, dao_factory, auth):
        self.dao_factory = dao_factory
        self.auth = auth
        self.parse_args()

    def get_arg_parser(self):
        parent = super().get_arg_parser()
        parser = argparse.ArgumentParser(parents = [parent], prog = 'admin.py add-user')
        parser.add_argument('-u', '--username', metavar='USERNAME', required=True)
        parser.add_argument('-r', '--rights', metavar='RIGHTS', required=True)
        parser.add_argument('-p', '--provide-password', action='store_true')
        return parser

    def __call__(self):
        password = None
        user_dao = self.dao_factory.get_user_dao()
        user = User(
            username = self.username,
            rights = ([UserRight.USER] +
                [UserRight.by_name(x) for x in self.rights.split(',')]),
            attributes = [])

        if self.provide_password:
            password = input_password()
        else:
            password = random_password()
            user.attributes.add(UserAttribute.PASSWORD_RESET_REQUIRED)

        user.passhash = self.auth.encrypt_password(password)
        user_dao.put(user)

        print('User %s created.' % user.username)

        if not self.provide_password:
            print()
            print('The user\'s initial password is "%s".' % password)
            print('They will be required to provide their own password on first login.')

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
