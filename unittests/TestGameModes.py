import json

from unittest import TestCase
from flask import Flask
from flask_controllers.GameModes import GameModes
from flask_helpers.VersionHelpers import VersionHelpers
from python_cowbull_server import app
from python_cowbull_server.Configurator import Configurator
from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.PersistenceEngine import PersistenceEngine


class TestGameModes(TestCase):
    def setUp(self):
        self.info = VersionHelpers()
        app.testing = True
        self.app = app.test_client()

        self.c = Configurator()
        self.c.execute_load(self.app.application)

        # Force use of File persister
        p = {"engine_name": "file", "parameters": {}}
        self.app.application.config["PERSISTER"] = PersistenceEngine(**p)

        if self.info.major < 3:
            self.json_raises = ValueError
        else:
            self.json_raises = json.JSONDecodeError

    def test_gms_init(self):
        GameModes()

    def test_gms_bad_init(self):
        p = self.app.application.config["PERSISTER"]
        self.app.application.config["PERSISTER"] = None
        try:
            GameModes()
        except ValueError as ve:
            self.assertIn("No persistence engine is defined", str(ve))
        self.app.application.config["PERSISTER"] = p

    def test_gms_get_game_modes(self):
        with self.app as c:
            response = c.get('/v1/modes')
            self.assertEqual(response.status, '200 OK')
            self.assertIn("Welcome to the CowBull game. The objective of this game", str(response.data))

    def test_gms_get_game_modes_text(self):
        with self.app as c:
            response = c.get('/v1/modes?textmode=true')
            text_modes = json.loads(response.data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(text_modes, ["Easy", "Normal", "Hard", "Hex"])
