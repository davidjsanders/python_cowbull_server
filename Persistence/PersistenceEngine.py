from Persistence.RedisPersist import RedisPersist
from Persistence.MongoPersist import MongoPersist
from Persistence.GCPStoragePersist import GCPStoragePersist


class PersistenceEngine(object):
    def __init__(self, **kwargs):
        engine_name = kwargs.get('engine_name', None)
        parameters = kwargs.get('parameters', None)

        if not engine_name or not parameters:
            raise ValueError(
                "'engine_name' and 'parameters' must be defined "
                "for the persistence engine"
            )
        if not isinstance(parameters, dict):
            raise TypeError(
                "'parameters' must be a dictionary of objects"
            )

        self._engine_name = engine_name
        self._parameters = parameters
        self._persister = None

        if self._engine_name.lower() == 'mongodb':
            self._persister = MongoPersist
        elif self._engine_name.lower() == 'gcpstorage':
            self._persister = GCPStoragePersist
        elif self._engine_name.lower() == 'redis':
            self._persister = RedisPersist
        else:
            raise ValueError(
                "The persistence engine provided ('{}') is "
                "unknown and not supported"
                    .format(
                    self.persister_config.engine_name
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
        return self._persister

    def __repr__(self):
        return "<persister>{}".format(self._engine_name)