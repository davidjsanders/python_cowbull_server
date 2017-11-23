from flask_helpers.ErrorHandler import ErrorHandler
import redis


class RedisPersist:
    _redis_connection = None

    def __init__(self, host="localhost", port=6379, db=0):
        self.handler = ErrorHandler(
            module="RedisPersist",
            method="__init__",
        )

        self.handler.log(message="Preparing redis connection")
        self._redis_connection = redis.StrictRedis(
            host=host,
            port=port,
            db=db
        )

        self.handler.log(message="Testing redis connection with dummy key")
        self._redis_connection.set('tmp_validate', 'tmp_validate', ex=60)

    def save(self, key=None, jsonstr=None):
        self.handler.method = "save"

        self.handler.log(message="Validating key: {}".format(key))
        if key is None:
            raise ValueError("Key must be present to persist game.")

        self.handler.log(message="Validating json: {}".format(jsonstr))
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")

        self.handler.log(message="Setting key {} in redis".format(key))
        self._redis_connection.set(str(key), str(jsonstr), ex=(60*60))
        self.handler.log(message="Key set.")

    def load(self, key=None):
        self.handler.method = "load"

        self.handler.log(message="Validating key: {}".format(key))
        if key is None:
            raise ValueError("Key must be present to execute_load game")

        self.handler.log(message="Fetching key: {}".format(key))
        return_result = self._redis_connection.get(key)
        if return_result is not None:
            if isinstance(return_result, bytes):
                return_result = str(return_result.decode('utf-8'))

        self.handler.log(message="Key {} returned: {}".format(key, return_result))
        return return_result
