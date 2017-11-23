from flask_helpers.ErrorHandler import ErrorHandler
from os import listdir
from os import getcwd
from sys import path
import importlib


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

        # Step 1 - Build path
        cwd = getcwd()
        extension_path = "{}/{}".format(cwd, "./PersistenceExtensions")
        path.append(extension_path)

        # Step 2 - get the persisters and choose the right one
        persisters = [file[:-3] for file in listdir(extension_path) if file.endswith(".py")]

        validators = [file.lower() for file in persisters]
        try:
            self._engine_name = persisters[validators.index(self._engine_name)]
            self._persister = importlib.import_module(self._engine_name)
            self.handler.log(message="Persistence engine set to {}".format(self._engine_name))
        except ValueError as v:
            self._engine_name = "RedisPersist"
            from Persistence import RedisPersist
            self._persister = RedisPersist
            self.handler.log(message="Persistence engine defaulted to Redis")
        except Exception as e:
            raise
        return

    @property
    def engine_name(self):
        return self._engine_name

    @property
    def parameters(self):
        return self._parameters

    @property
    def persister(self):
        return self._persister.Persister(
            **self.parameters
        )

    def __repr__(self):
        return "<persister>{}".format(self._engine_name)