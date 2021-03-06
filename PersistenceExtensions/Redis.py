from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.AbstractPersister import AbstractPersister
from redis.sentinel import Sentinel, MasterNotFoundError, SlaveNotFoundError, ResponseError
import redis


class Persister(AbstractPersister):
    _redis_connection = None

    def __init__(
        self, 
        host="localhost", 
        password="",
        port=6379, 
        master_port=26379, 
        db=0
    ):
        super(Persister, self).__init__()

        self.handler.module="Redis Persister"
        self.handler.log(message="Preparing redis connection")

        master_node = None
        sentinel = None
        # Removed as per http://sonarqube:9000/project/issues?id=cowbull_server&issues=AWiRMKBbaAhZ-jY-ujHo&open=AWiRMKBbaAhZ-jY-ujHo
        # slave_nodes = [(host, port)]

        self.handler.log(message="Host: {0}, Port: {1}".format(host, port))

        try:
            self.handler.log(message="Checking if redis instance passed is a cluster")
            sentinel = Sentinel([(host, master_port)], socket_timeout=0.1)
            master_node = sentinel.discover_master('redis')
            self.handler.log(message="It is a cluster. Setting master node")
        except MasterNotFoundError:
            self.handler.log(message="No cluster found; using single redis instance only")
        except ResponseError:
            self.handler.log(message="No cluster found; using single redis instance only")
        except Exception:
            raise

        if master_node:
            self.handler.log(message="Setting redis master for writes")
            self._redis_master = sentinel.master_for("redis", socket_timeout=0.1)
            self._redis_connection = sentinel.slave_for("redis", socket_timeout=0.1)
        else:
            self._redis_connection = redis.StrictRedis(
                host=host,
                port=port,
                password=password,
                db=db
            )
            self.handler.log(message="Pointing redis master to connection")
            self._redis_master = self._redis_connection

    @property
    def redis_connection(self):
        return self._redis_connection or None

    def save(self, key=None, jsonstr=None):
        super(Persister, self).save(key=key, jsonstr=jsonstr)
        try:
            self._redis_master.set(str(key), str(jsonstr), ex=(60*60))
        except redis.exceptions.ConnectionError as rce:
            raise KeyError("Unable to connect to the Redis persistence engine: {}".format(str(rce)))
        self.handler.log(message="Key set.")

    def load(self, key=None):
        super(Persister, self).load(key=key)

        self.handler.log(message="Fetching key: {}".format(key))
        try:
            return_result = self._redis_connection.get(key)
            if not return_result:
                raise KeyError("Unable to load key {}".format(key))
        except redis.exceptions.ConnectionError as rce:
            raise KeyError("Unable to connect to the Redis persistence engine: {}".format(str(rce)))
        except Exception as e:
            raise KeyError("An exception occurred: {}".format(str(e)))

        # http://sonarqube:9000/project/issues?id=cowbull_server&issues=AWiRMKBcaAhZ-jY-ujHp&open=AWiRMKBcaAhZ-jY-ujHp
        if return_result is not None and isinstance(return_result, bytes):
                return_result = str(return_result.decode('utf-8'))

        self.handler.log(message="Key {} returned: {}".format(key, return_result))
        return return_result
