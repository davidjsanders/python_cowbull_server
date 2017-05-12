import redis


class RedisPersist:
    _redis_connection = None

    def __init__(self, host="localhost", port=6379, db=0):
        self._redis_connection = redis.StrictRedis(
            host=host,
            port=port,
            db=db
        )
        self._redis_connection.set('tmp_validate', 'tmp_validate')

    def save(self, key=None, jsonstr=None):
        if key is None:
            raise ValueError("Key must be present to persist game.")
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")
        self._redis_connection.set(str(key), str(jsonstr), ex=(60*60))

    def load(self, key=None):
        if key is None:
            raise ValueError("Key must be present to load game")
        return_result = self._redis_connection.get(key)
        if return_result is not None:
            if isinstance(return_result, bytes):
                return_result = str(return_result.decode('utf-8'))
        return return_result
