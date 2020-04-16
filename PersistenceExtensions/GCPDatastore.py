from datetime import datetime
from flask_helpers.ErrorHandler import ErrorHandler
from google.cloud import datastore
from Persistence.AbstractPersister import AbstractPersister


class Persister(AbstractPersister):
    def __init__(self):
        super(Persister, self).__init__()

        self.handler.module="GCPDatastorePersist"
        self.handler.log(message="Preparing datastore client")

        self.datastore_client = datastore.Client()
        self.kind = "save"

        key = "validation-save-ignored"
        current_date = "{}".format(datetime.now())

        # Get a datastore key
        try:
            self.handler.log(message="Creating datastore key: {}".format(key))
            _key = self.datastore_client.key(self.kind, key)
        except Exception as e:
            print("Exception while getting datastore client - {}".format(str(e)))
            self.handler.log(message="In GCPDatastorePersist __init__ an exception occurred: {}".format(repr(e)))
            raise

        # Create an entity
        try:
            _save = datastore.Entity(key=_key)
            _save['game'] = "validation: {}".format(current_date)
        except Exception as e:
            print("Exception while getting datastore Entity - {}".format(str(e)))
            self.handler.log(message="In GCPDatastorePersist __init__ an exception occurred: {}".format(repr(e)))
            raise

        # Update the DB
        try:
            self.datastore_client.put(_save)
        except Exception as e:
            print("Exception while putting data - {}".format(str(e)))
            self.handler.log(message="In GCPDatastorePersist __init__ an exception occurred: {}".format(repr(e)))
            raise

        self.handler.log(message="Datastore client fetched")

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)

        self.handler.log(message="Creating datastore key: {}".format(key))
        try:
            _key = self.datastore_client.key(self.kind, key)
        except Exception as e:
            print("Exception - {}".format(str(e)))
            return self.handler.error(status=500, message="Exception {}".format(repr(e)))

        if not _key:
            raise ValueError("The key was returned as None!")

        self.handler.log(message="Fetching entity: {}".format(_key))
        try:
            _save = datastore.Entity(key=_key)
        except Exception as e:
            print("Exception - {}".format(str(e)))
            return self.handler.error(status=500, message="Exception {}".format(repr(e)))

        _save["game"] = jsonstr
        self.handler.log(message="Writing game to GCP Datastore")
        try:
            self.datastore_client.put(_save)
        except Exception as e:
            print("Exception - {}".format(str(e)))
            return self.handler.error(status=500, message="Exception {}".format(repr(e)))

    def load(self, key=None):
        super(Persister, self).load(key=key)

        self.handler.log(message="Calling datastore query on key: {}".format(key))
        self.handler.log(message="Creating datastore key: {}".format(key))
        try:
            _key = self.datastore_client.key(self.kind, key)
        except Exception as e:
            print("Exception - {}".format(str(e)))
            return self.handler.error(status=500, message="Exception {}".format(repr(e)))

        try:
            save = self.datastore_client.get(_key)
            if not save:
                raise ValueError("Key not found")
        except Exception as e:
            print("Exception - {}".format(str(e)))
            return self.handler.error(status=500, message="Exception {}".format(repr(e)))

        self.handler.log(message="Query returned: {}".format(save))
        self.handler.log(message="Query returned: {}".format(save["game"]))
        return save["game"]
