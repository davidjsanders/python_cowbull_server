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
        self.handler.log(
            module="AbstractPersister",
            method="load",
            message="Base class processing - Nothing at present"
        )

    @abc.abstractmethod
    def save(self, key=None, jsonstr=None):
        self.handler.log(
            module="AbstractPersister",
            method="save",
            message="Base class processing - Nothing at present"
        )

