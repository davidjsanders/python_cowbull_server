from flask_helpers.ErrorHandler import ErrorHandler
import json
import pymongo


class Persister:
    def __init__(self, host="localhost", port=27017, db="cowbull"):
        self.handler = ErrorHandler(
            module="MongoPersist",
            method="__init__",
        )

        self.handler.log(message="Persistence engine MongoDB establishing client to database: {} {}.".format(host, port))
        self.connection = pymongo.MongoClient(host=host, port=port)

        self.handler.log(message="Establishing connection.")
        self.mdb = self.connection[db]

        self.handler.log(message="Persistence engine initialization complete.")

    def save(self, key=None, jsonstr=None):
        self.handler.method="save"

        self.handler.log(message="Validating key: {}".format(key))
        if key is None:
            raise ValueError("Key must be present to persist game.")

        self.handler.log(message="Validating jsonstr: {}".format(jsonstr))
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")

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
        self.handler.method="load"

        self.handler.log(message="Validating key: {}".format(key))
        if key is None:
            raise ValueError("Key must be present to execute_load game")

        self.handler.log(message="Connecting to the games database")
        games = self.mdb.games

        self.handler.log(message="Finding key {}".format(key))
        return_result = games.find_one({"_id": key})

        if return_result:
            self.handler.log(message="Key {} returned {}".format(key, return_result["game"]))
            return json.dumps(return_result["game"])

        self.handler.log(message="Key {} was not found! An exception will be raised.".format(key))
        return return_result
