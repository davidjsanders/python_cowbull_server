from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.AbstractPersister import AbstractPersister
import redis


class Persister(AbstractPersister):
    _redis_connection = None

    def __init__(self, host="localhost", port=6379, db=0):
        super(Persister, self).__init__()

        self.handler.module="Redis Persister"
        self.handler.log(message="Preparing redis connection")
        self._redis_connection = redis.StrictRedis(
            host=host,
            port=port,
            db=db
        )

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)
        try:
            self._redis_connection.set(str(key), str(jsonstr), ex=(60*60))
        except redis.exceptions.ConnectionError as rce:
            raise KeyError("Unable to connect to the Redis persistence engine: {}".format(str(rce)))
        self.handler.log(message="Key set.")

    def load(self, key=None):
        super(Persister, self).load(key=key)

        self.handler.log(message="Fetching key: {}".format(key))
        return_result = self._redis_connection.get(key)

        if return_result is not None:
            if isinstance(return_result, bytes):
                return_result = str(return_result.decode('utf-8'))

        self.handler.log(message="Key {} returned: {}".format(key, return_result))
        return return_result
