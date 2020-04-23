import json

from unittest import TestCase
from flask import Flask
from flask_controllers.GameServerController import GameServerController
from flask_helpers.VersionHelpers import VersionHelpers
from python_cowbull_server import app
from python_cowbull_server.Configurator import Configurator
from flask_helpers.ErrorHandler import ErrorHandler
from Persistence.PersistenceEngine import PersistenceEngine


class TestGameServerController(TestCase):
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

    def test_gsc_init(self):
        GameServerController()

    def test_gsc_bad_init(self):
        self.app.application.config["PERSISTER"] = None
        try:
            GameServerController()
        except ValueError as ve:
            self.assertIn("No persistence engine is defined", str(ve))

    def test_gsc_valid_init(self):
        gsc = GameServerController()
        self.assertIsNone(gsc.game_version)
        self.assertIsInstance(gsc.handler, ErrorHandler)

    def test_gsc_get_game(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status, '200 OK')

    def test_gsc_get_game_bad_mode(self):
        gsc = GameServerController()
        with self.app as c:
            response = c.get('/v1/game?mode=reallyreallytough')
            self.assertEqual(response.status, '400 BAD REQUEST')
            self.assertIn("Mode reallyreallytough not found", str(response.data))

    def test_gsc_get_game_bad_persister(self):
        p = self.app.application.config["PERSISTER"]
        with self.app:
            with self.assertRaises(TypeError):
                self.app.application.config["PERSISTER"] = PersistenceEngine(
                        engine_name="foobar",
                        parameters={
                            "host": "foobar", 
                            "port": 27017, 
                            "db": "cowbull"
                        }
                    )
        self.app.application.config["PERSISTER"] = p

    def test_gsc_get_game_no_persister(self):
        p = self.app.application.config["PERSISTER"]
        with self.app as c:
            with self.assertRaises(KeyError):
                self.app.application.config["PERSISTER"] = PersistenceEngine(
                        engine_name="redis",
                        parameters={
                            "host": "local", 
                            "port": 6379, 
                            "db": "cowbull"
                        }
                    )
                c.get('/v1/game')
        self.app.application.config["PERSISTER"] = p

    def test_gsc_get_game_badparam_persister(self):
        p = self.app.application.config["PERSISTER"]
        with self.app:
            with self.assertRaises(TypeError):
                self.app.application.config["PERSISTER"] = PersistenceEngine(
                        engine_name="redis",
                        parameters={
                            "host": "local", 
                            "port": 6379, 
                            "db": "cowbull",
                            "foo": "bar"
                        }
                    )
        self.app.application.config["PERSISTER"] = p

    def test_gsc_post_game(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '200')
            key = json.loads(response.data)["key"]
            game_data = {
                "key": key,
                "digits": [0, 1, 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '200')

    def test_gsc_post_bad_key(self):
        with self.app as c:
            key = '1234'
            game_data = {
                "key": key,
                "digits": [0, 1, 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("The request must contain a valid game key", str(response.data))

    def test_gsc_post_bad_digits(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '200')
            key = json.loads(response.data)["key"]
            game_data = {
                "key": key,
                "digits": ['X', 'Y', 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')

    def test_gsc_post_no_digits(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '200')
            key = json.loads(response.data)["key"]
            game_data = {
                "key": key
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("The request must contain an array of digits", str(response.data))

    def test_gsc_post_num_digits(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '200')
            key = json.loads(response.data)["key"]
            game_data = {
                "key": key,
                "digits": [0, 1, 2, 3, 4, 5]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("The DigitWord objects are of different lengths", str(response.data))

    def test_gsc_post_hilo_digits(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '200')
            key = json.loads(response.data)["key"]
            game_data = {
                "key": key,
                "digits": [-10, 21, 32, 43]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("A digit must be a string representation or integer of a number", str(response.data))

    def test_gsc_post_type_digits(self):
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '200')
            key = json.loads(response.data)["key"]
            game_data = {
                "key": key,
                "digits": {"foo": "bar"}
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("A digit must be a string representation or integer of a number", str(response.data))

    def test_gsc_post_no_json(self):
        with self.app as c:
            response = c.post(
                '/v1/game',
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("For some reason the json_dict is None!", str(response.data))

    def test_gsc_post_bad_json(self):
        with self.app as c:
            response = c.post(
                '/v1/game',
                data=json.dumps({"keys": "1234"}),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("For some reason the json_dict does not contain a key", str(response.data))

    def test_gsc_post_bad_gamekey(self):
        with self.app as c:
            key = '1234'
            game_data = {
                "key": key,
                "digits": ['X', 'Y', 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("Unable to open the key file", str(response.data))

    def test_gsc_post_badtype_gamekey(self):
        with self.app as c:
            key = 1234
            game_data = {
                "key": key,
                "digits": ['X', 'Y', 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("For some reason the json_dict does not contain a key!", str(response.data))

    def test_gsc_post_no_gamekey(self):
        with self.app as c:
            game_data = {
                "digits": ['X', 'Y', 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("For some reason the json_dict does not contain a key", str(response.data))

    def test_gsc_post_type_gamekey(self):
        with self.app as c:
            game_data = {
                "key": None,
                "digits": ['X', 'Y', 2, 3]
            }
            response = c.post(
                '/v1/game', 
                data=json.dumps(game_data),
                content_type="application/json"
            )
            self.assertEqual(response.status[0:3], '400')
            self.assertIn("For some reason the json_dict does not contain a key!", str(response.data))
