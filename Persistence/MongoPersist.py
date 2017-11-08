import json
import pymongo
import logging


class MongoPersist:
    def __init__(self, host="localhost", port=27017, db="cowbull"):
        self.connection = pymongo.MongoClient(host=host, port=port)
        self.mdb = self.connection[db]
        logging.info("Persistence engine called: MongoDB")

    def save(self, key=None, jsonstr=None):
        if key is None:
            raise ValueError("Key must be present to persist game.")
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")

        games = self.mdb.games
        game = games.find_one({"_id": key})

        if game:
            games.update_one(
                {"_id": key},
                {"$set":
                    {
                        "game": json.loads(jsonstr)
                    }
                }
            )
        else:
            games.insert_one({"_id": key, "game": json.loads(jsonstr)})

    def load(self, key=None):
        if key is None:
            raise ValueError("Key must be present to execute_load game")

        games = self.mdb.games

        return_result = games.find_one({"_id": key})
        if return_result:
            return json.dumps(return_result["game"])
        return return_result
