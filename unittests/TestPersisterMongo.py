import json
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

from unittest import TestCase
from PersistenceExtensions.MongoDB import Persister

class TestPersisterMongo(TestCase):
    def setUp(self):
        self.p = Persister(
            host="foobar", 
            port=27017, 
            db="cowbull",
            server_selection_timeout_ms=1000
        )

    def test_mp_bad_save(self):
        with self.assertRaises(ServerSelectionTimeoutError):
            self.p.save(key="foo",jsonstr="bar")

    def test_mp_bad_load(self):
        with self.assertRaises(KeyError):
            self.p.load(key="foo")
