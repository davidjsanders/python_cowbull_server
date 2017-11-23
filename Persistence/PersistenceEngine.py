from flask_helpers.ErrorHandler import ErrorHandler


class PersistenceEngine(object):
    valid_engines = ["mongodb", "redis", "gcpstorage", "gcpdatastore"]

    def __init__(self, **kwargs):
        self.handler = ErrorHandler(
            module="PersistenceEngine",
            method="__init__"
        )

        self.handler.log(message="Getting persistence engine arguments")
        engine_name = kwargs.get('engine_name', None)
        parameters = kwargs.get('parameters', None)

        if not engine_name:
            raise ValueError(
                "'engine_name' must be defined for the persistence engine"
            )
        if not isinstance(parameters, dict):
            raise TypeError(
                "'parameters' must be a dictionary of objects"
            )

        self._engine_name = engine_name
        self._parameters = parameters
        self._persister = None

        if self._engine_name.lower() == 'mongodb':
            self.handler.log(message="Setting persistence engine to MongoDB")
            from Persistence.MongoPersist import MongoPersist
            self._persister = MongoPersist
        elif self._engine_name.lower() == 'gcpstorage':
            self.handler.log(message="Setting persistence engine to GCP Storage")
            from Persistence.GCPStoragePersist import GCPStoragePersist
            self._persister = GCPStoragePersist
        elif self._engine_name.lower() == 'gcpdatastore':
            self.handler.log(message="Setting persistence engine to GCP Datastore")
            from Persistence.GCPDatastorePersist import GCPDatastorePersist
            self._persister = GCPDatastorePersist
        elif self._engine_name.lower() == 'redis':
            self.handler.log(message="Setting persistence engine to Redis")
            from Persistence.RedisPersist import RedisPersist
            self._persister = RedisPersist
        else:
            self.handler.log(message="Persistence engine {} provided is unknown!".format(self._engine_name))
            raise ValueError(
                "The persistence engine provided ('{}') is "
                "unknown and not supported. Valid vaules are: "
                "{}"
                    .format(
                        self._engine_name,
                        PersistenceEngine.valid_engines
                )
            )


    @property
    def engine_name(self):
        return self._engine_name

    @property
    def parameters(self):
        return self._parameters

    @property
    def persister(self):
        return self._persister(
            **self.parameters
        )

    def __repr__(self):
        return "<persister>{}".format(self._engine_name)