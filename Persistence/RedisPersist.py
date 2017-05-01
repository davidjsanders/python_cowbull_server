import redis


class RedisPersist:
    _server = {
        "db": 0,
        "port": 6379,
        "host": "localhost"
    }
    _redis_connection = None

    def __init__(self):
        self._redis_connection = redis.StrictRedis(
            host=self._server["host"],
            port=self._server["port"],
            db=self._server["db"]
        )
        self._redis_connection.set('tmp_validate', 'tmp_validate')

    def save(self, key=None, jsonstr=None):
        if key is None:
            raise ValueError("Key must be present to persist game.")
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")
        self._redis_connection.set(key, jsonstr)

    def load(self, key=None):
        if key is None:
            raise ValueError("Key must be present to load game")
        return_result = self._redis_connection.get(key)
        if return_result is not None:
            return_result = return_result.decode('utf-8')
        return return_result
