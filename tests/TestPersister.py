import json
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

from unittest import TestCase
from Persistence.PersistenceEngine import PersistenceEngine

class TestPersister(TestCase):
    def test_bad_engine(self):
        with self.assertRaises(TypeError):
            PersistenceEngine(
                engine_name="foobar",
                parameters={
                    "host": "foobar", 
                    "port": 27017, 
                    "db": "cowbull"
                }
            )

    def test_bad_parameters(self):
        with self.assertRaises(TypeError):
            PersistenceEngine(
                engine_name="foobar",
                parameters=["foobar", 27017, "cowbull"]
            )

    def test_bad_engine_name(self):
        with self.assertRaises(ValueError):
            PersistenceEngine(
                engine_name=None,
                parameters=["foobar", 27017, "cowbull"]
            )

    def test_bad_abstract(self):
        with self.assertRaises(TypeError):
            PersistenceEngine(
                engine_name="TestOnly",
                parameters={
                    "host": "foobar", 
                    "port": 27017, 
                    "db": "cowbull"
                }
            )

