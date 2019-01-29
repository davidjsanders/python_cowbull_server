from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.AbstractPersister import AbstractPersister
import json
import pymongo


class Persister(AbstractPersister):
    def __init__(
        self, 
        host="localhost", 
        port=27017, 
        db="cowbull",
        server_selection_timeout_ms=30000
    ):
        super(Persister, self).__init__()

        self.handler.module="MongoDB Persister"
        self.handler.log(message="Persistence engine MongoDB establishing client to database: {} {}.".format(host, port))
        self.connection = pymongo.MongoClient(
            host=host, 
            port=port,
            serverSelectionTimeoutMS=server_selection_timeout_ms
            )

        self.handler.log(message="Establishing connection.")
        self.mdb = self.connection[db]

        self.handler.log(message="Persistence engine initialization complete.")

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)

        self.handler.log(message="Using the games database")
        games = self.mdb.games

        self.handler.log(message="Checking if {} already exists".format(key))
        game = games.find_one({"_id": key})

        if game:
            self.handler.log(message="Key {} exists, so update".format(key))
            games.update_one(
                {"_id": key},
                {"$set":
                    {
                        "game": json.loads(jsonstr)
                    }
                }
            )
        else:
            self.handler.log(message="Key {} does not exist, so insert.".format(key))
            games.insert_one({"_id": key, "game": json.loads(jsonstr)})

    def load(self, key=None):
        super(Persister, self).load(key=key)

        self.handler.log(message="Connecting to the games database")
        games = self.mdb.games

        self.handler.log(message="Finding key {}".format(key))
        return_result = games.find_one({"_id": key})

        if return_result:
            self.handler.log(message="Key {} returned {}".format(key, return_result["game"]))
            return json.dumps(return_result["game"])

        self.handler.log(message="Key {} was not found! An exception will be raised.".format(key))
        return return_result
