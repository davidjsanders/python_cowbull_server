import json

from unittest import TestCase
from flask import Flask
from flask_controllers.GameServerController import GameServerController
from flask_helpers.VersionHelpers import VersionHelpers
from python_cowbull_server import app
from python_cowbull_server.Configurator import Configurator
from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.PersistenceEngine import PersistenceEngine


class TestHealthCheck(TestCase):
    def test_hc_get_health(self):
        self.info = VersionHelpers()
        app.testing = True
        self.app = app.test_client()

        self.c = Configurator()
        self.c.execute_load(self.app.application)

        # Force use of File persister
        p = {"engine_name": "file", "parameters": {}}
        self.app.application.config["PERSISTER"] = PersistenceEngine(**p)
        with self.app as c:
            response = c.get('/v1/health')
            self.assertEqual(response.status[0:3], '200')
            health = json.loads(response.data)
            self.assertEqual(health["health"], "ok")

