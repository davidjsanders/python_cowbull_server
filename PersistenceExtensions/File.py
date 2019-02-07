from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.AbstractPersister import AbstractPersister
import io
import json
import pymongo


class Persister(AbstractPersister):
    def __init__(
        self
    ):
        super(Persister, self).__init__()

        self.handler.module="File Persister"
        self.handler.log(message="Preparing file system")


    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)

        filename = '/tmp/{}.cow'.format(key)

        self.handler.log(message="Opening file: {}".format(filename))
        try:
            f=open(filename, 'w')
        except IOError as ioe:
            raise KeyError("Unable to open the key file: {}".format(str(filename)))

        self.handler.log(message="Writing key {} and json {} to file: {}".format(key, jsonstr, filename))
        try:
            f.write(jsonstr)
        except IOError as ioe:
            raise KeyError("Unable to write to the key file: {}".format(str(filename)))
        finally:
            f.close()
        self.handler.log(message="Key set.")

    def load(self, key=None):
        super(Persister, self).load(key=key)

        filename = '/tmp/{}.cow'.format(key)

        self.handler.log(message="Opening file: {}".format(filename))
        try:
            f=open(filename, 'r')
        except IOError as ioe:
            raise KeyError("Unable to open the key file: {}".format(str(filename)))

        self.handler.log(message="Reading key {} from file: {}".format(key, filename))
        json_return = None
        try:
            json_return=f.read()
        except IOError as ioe:
            raise KeyError("Unable to open the key file: {}".format(str(filename)))
        finally:
            f.close()

        self.handler.log(message="Fetched {} from key {} in file: {}".format(json_return, key, filename))
        return json_return
