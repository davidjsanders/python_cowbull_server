from flask_helpers.ErrorHandler import ErrorHandler
from google.appengine.ext import ndb
from Persistence.AbstractPersister import AbstractPersister


class CowbullSaveGame(ndb.Model):
    game = ndb.StringProperty()

    @classmethod
    def query_game(cls, key):
        return cls.query(ancestor=key)


class Persister(AbstractPersister):
    def __init__(self):
        super(Persister, self).__init__()

        self.handler.module="GCPDatastorePersist"
        self.handler.log(message="Preparing datastore client")

        try:
            _key = ndb.Key("CowbullSaveGame", "1234")
            sg = CowbullSaveGame(key=_key, game="This is a test")
            sg.put()
        except Exception as e:
            self.handler.log(message="In GCPDatastorePersist __init__ an exception occurred: {}".format(repr(e)))

        self.handler.log(message="Datastore client fetched")
        self.kind = 'CowbullSaveGame'

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)

        self.handler.log(message="Creating ndb key: {}".format(key))
        _key = ndb.Key(self.kind, key)
        if not _key:
            raise ValueError("The key was returned as None!")

        self.handler.log(message="Saving game with key: {}".format(key))
        sg = CowbullSaveGame(key=_key, game=jsonstr)

        self.handler.log(message="Putting key to datastore")
        sg.put()

    def load(self, key=None):
        super(Persister, self).load(key=key)

        self.handler.log(message="Calling datastore query on key: {}".format(key))
        try:
            _key = ndb.Key(self.kind, key)
            save_games = CowbullSaveGame.query_game(key=_key).fetch(1)
            if not save_games:
                raise ValueError("Key not found")
        except Exception as e:
            return self.handler.error(status=500, message="Exception {}".format(repr(e)))

        return save_games[0].game
