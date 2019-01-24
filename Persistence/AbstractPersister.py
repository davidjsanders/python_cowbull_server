#
# For compatibility with Python 2.x and 3.x, we use a specific means of
# setting up an abstract class. See the stackoverflow question at
#
# https://stackoverflow.com/questions/35673474/
#   using-abc-abcmeta-in-a-way-it-is-compatible-both-with-python-2-7-and-python-3-5
#
# DO NOT MODIFY THE CODE WITHOUT UNDERSTANDING THE IMPACT UPON PYTHON 2.7
#
import abc
from flask_helpers.ErrorHandler import ErrorHandler


# Force compatibility with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class AbstractPersister(ABC):
    def __init__(self):
        self.handler = ErrorHandler(
            module="AbstractPersister",
            method="__init__",
        )

    @abc.abstractmethod
    def load(self, key=None):
        save_module_name = self.handler.module
        self.handler.module = "Base Persister"
        self.handler.method = "load"
        self.handler.log(message="Validating key: {}".format(key))
        if key is None:
            raise ValueError("Key must be present to load a persisted game.")
        self.handler.module = save_module_name

    @abc.abstractmethod
    def save(self, key=None, jsonstr=None):
        save_module_name = self.handler.module
        self.handler.module = "Base Persister"
        self.handler.method = "save"

        self.handler.log(message="Base persistence processing")

        self.handler.log(message="Validating key: {}".format(key))
        if key is None:
            raise ValueError("Key must be present to persist game.")

        self.handler.log(message="Validating json: {}".format(jsonstr))
        if jsonstr is None:
            raise ValueError("JSON is badly formed or not present")

        self.handler.log(message="Saving key {} with {} to persister".format(key, jsonstr))

        self.handler.module = save_module_name
