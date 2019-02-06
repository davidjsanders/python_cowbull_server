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
        if self.info.major < 3:
            self.json_raises = ValueError
        else:
            self.json_raises = json.JSONDecodeError

    def test_gsc_init(self):
        GameServerController()

    def test_gsc_bad_init(self):
        self.app.application.config["PERSISTER"] = None
        with self.assertRaises(ValueError):
            GameServerController()

    def test_gsc_valid_init(self):
        gsc = GameServerController()
        self.assertIsNone(gsc.game_version)
        self.assertIsInstance(gsc.handler, ErrorHandler)

    def test_gsc_get_game(self):
        gsc = GameServerController()
        with self.app as c:
            response = c.get('/v1/game')
            self.assertEqual(response.status, '200 OK')

    def test_gsc_get_game_bad_mode(self):
        gsc = GameServerController()
        with self.app as c:
            response = c.get('/v1/game?mode=reallyreallytough')
            self.assertEqual(response.status, '400 BAD REQUEST')

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
            self.app.application.config["PERSISTER"] = PersistenceEngine(
                    engine_name="redis",
                    parameters={
                        "host": "local", 
                        "port": 6379, 
                        "db": "cowbull"
                    }
                )
            response = c.get('/v1/game')
            self.assertEqual(response.status[0:3], '500')
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
            self.assertIn("The game key (1234) was not found", str(response.data))

    def test_gsc_post_no_gamekey(self):
        with self.app as c:
            key = '1234'
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

    # def test_gc_new(self):
    #     g = GameController()
    #     self.assertIsInstance(g, GameController)

    # def test_gc_new_badmode(self):
    #     with self.assertRaises(ValueError):
    #         GameController(mode="foobar")

    # def test_gc_new_game_modes(self):
    #     mode_list = [
    #         GameMode(
    #             mode="test1",
    #             priority=5,
    #         ),
    #         GameMode(
    #             mode="test2",
    #             priority=6,
    #         )
    #     ]
    #     g = GameController(game_modes=mode_list)
    #     modes = g.game_mode_names
    #     self.assertTrue("test1" in modes)
    #     self.assertTrue("test2" in modes)
    #     self.assertFalse("test3" in modes)

    # def test_gc_new_game_direct(self):
    #     g = GameController()
    #     g._new_game(
    #         GameMode(
    #             mode="test1",
    #             priority=5,
    #         )
    #     )

    # def test_gc_new_game_direct_default_mode(self):
    #     g = GameController()
    #     g._new_game(mode=None)
    #     self.assertEqual(g.game.mode.mode, g.find(0).mode)

    # def test_gc_new_game_direct_badmode(self):
    #     g = GameController()
    #     with self.assertRaises(TypeError):
    #         g._new_game(
    #             {
    #                 "mode": "test1",
    #                 "priority": 5,
    #             }
    #         )

    # def test_gc_load_game_modes(self):
    #     mode_list = [
    #         GameMode(
    #             mode="test1",
    #             priority=5,
    #         ),
    #         GameMode(
    #             mode="test2",
    #             priority=6,
    #         )
    #     ]
    #     g = GameController()
    #     g.load_modes(input_modes=mode_list)
    #     modes = g.game_mode_names
    #     self.assertTrue("test1" in modes)
    #     self.assertTrue("test2" in modes)

    # def test_gc_load_game_modes_nolist(self):
    #     mode_list = \
    #         GameMode(
    #             mode="test1",
    #             priority=5,
    #         )
    #     g = GameController()
    #     with self.assertRaises(TypeError):
    #         g.load_modes(input_modes=mode_list)

    # def test_gc_load_game_modes_badlist(self):
    #     mode_list = ["normal", "hard"]
    #     g = GameController()
    #     with self.assertRaises(TypeError):
    #         g.load_modes(input_modes=mode_list)

    # def test_gc_load_game(self):
    #     g = GameController()
    #     with self.assertRaises(TypeError):
    #         g._load_game({"gameid":123})

    # def test_gc_new_game_json_normal(self):
    #     json_string = '{' \
    #                       '"answer": [9, 6, 9, 4], ' \
    #                       '"guesses_made": 0, "ttl": 3600, ' \
    #                       '"status": "playing", ' \
    #                       '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
    #                       '"mode": ' \
    #                         '{"help_text": ' \
    #                             '"This is the normal (default) game. You need to guess 4 ' \
    #                             'digits in the right place and each digit must be a whole ' \
    #                             'number between 0 and 9. There are 10 tries to guess the ' \
    #                             'correct answer.", ' \
    #                         '"guesses_allowed": 10, ' \
    #                         '"instruction_text": ' \
    #                             '"Enter 4 digits, each digit between 0 and 9 (0, 1, 2, 3, 4, ' \
    #                             '5, 6, 7, 8, and 9).", ' \
    #                         '"digit_type": 0, ' \
    #                         '"priority": 2, ' \
    #                         '"digits": 4, ' \
    #                         '"mode": "Normal"}' \
    #                   '}'
    #     g = GameController(game_json=json_string, mode="Normal")
    #     self.assertEqual(g.game.key, "12345678-0123-abcd-1234-0987654321fe")
    #     self.assertEqual(g.game.guesses_remaining, 10)
    #     self.assertEqual(g.game.guesses_made, 0)
    #     self.assertEqual(g.game.answer.word, [9, 6, 9, 4])

    # def test_gc_new_game_json_test1(self):
    #     json_string = '{' \
    #                     '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
    #                     '"answer": [4, 2, 0, 0], ' \
    #                     '"mode": {' \
    #                         '"guesses_allowed": 2, ' \
    #                         '"digit_type": 0, ' \
    #                         '"priority": 5, ' \
    #                         '"mode": "test1", ' \
    #                         '"instruction_text": "None", ' \
    #                         '"help_text": "None", ' \
    #                         '"digits": 4' \
    #                     '}, ' \
    #                     '"guesses_made": 0, ' \
    #                     '"ttl": 3600, ' \
    #                     '"status": "playing"' \
    #                   '}'
    #     g = GameController(game_json=json_string)
    #     self.assertEqual(g.game.key, "12345678-0123-abcd-1234-0987654321fe")
    #     self.assertEqual(g.game.guesses_remaining, 2)
    #     self.assertEqual(g.game.guesses_made, 0)
    #     self.assertEqual(g.game.answer.word, [4, 2, 0, 0])

    # def test_gc_load(self):
    #     g = GameController()
    #     g2 = GameController()
    #     g2.load(g.save())
    #     self.assertEqual(g.save(), g2.save())

    # def test_gc_load_bad_json(self):
    #     json_string = ''
    #     with self.assertRaises(self.json_raises):
    #         GameController(game_json=json_string)

    # def test_gc_load_bad_mode(self):
    #     json_string = '{' \
    #                     '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
    #                     '"answer": [4, 0], ' \
    #                     '"smode": {' \
    #                         '"guesses_allowed": 2, ' \
    #                         '"digit_type": 0, ' \
    #                         '"priority": 5, ' \
    #                         '"mode": "test1", ' \
    #                         '"instruction_text": "None", ' \
    #                         '"help_text": "None", ' \
    #                         '"digits": 4' \
    #                     '}, ' \
    #                     '"guesses_made": 0, ' \
    #                     '"ttl": 3600, ' \
    #                     '"status": "playing"' \
    #                   '}'
    #     with self.assertRaises(ValueError):
    #         g = GameController()
    #         g._load_game(json_string)

    # def test_gc_load_bad_data(self):
    #     json_string = '{' \
    #                     '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
    #                     '"answer": [4, 0], ' \
    #                     '"mode": {' \
    #                         '"guesses_allowed": 2, ' \
    #                         '"digit_type": 0, ' \
    #                         '"priority": 5, ' \
    #                         '"mode": "test1", ' \
    #                         '"instruction_text": "None", ' \
    #                         '"help_text": "None", ' \
    #                         '"digits": 4' \
    #                     '}, ' \
    #                     '"guesses_made": 0, ' \
    #                     '"ttl": 3600, ' \
    #                     '"status": "playing"' \
    #                   '}'
    #     with self.assertRaises(ValueError):
    #         GameController(game_json=json_string)

    # def test_gc_mode_names(self):
    #     g = GameController()
    #     modes = g.game_mode_names
    #     self.assertIsInstance(modes,list)

    # def test_gc_guess_once(self):
    #     g = GameController()
    #     r = g.guess(0,0,0,0)
    #     bulls = r.get("bulls", None)
    #     self.assertIsNot(bulls, None)

    # def test_gc_guess_win_game(self):
    #     g = GameController()
    #     ans = g.game.answer.word
    #     r = g.guess(*ans)
    #     self.assertEqual(r["bulls"], 4)

    # def test_gc_guess_with_cows(self):
    #     g = GameController()
    #     ans = g.game.answer.word
    #     ans.reverse()
    #     r = g.guess(*reversed(ans))
    #     self.assertTrue(r["cows"] > 0 and r["bulls"] != 4)

    # def test_gc_guess_lose_game(self):
    #     g = GameController()
    #     for i in range(10):
    #         g.guess(0,0,0,0)
    #     r = g.guess(0,0,0,0)
    #     self.assertIsNone(r.get("bulls"))

    # def test_gc_guess_no_game(self):
    #     g = GameController()
    #     g.game = None
    #     with self.assertRaises(ValueError):
    #         g.guess(1,2,3,4)

    # def test_gc_check_game_nomore_turns(self):
    #     response_object = {
    #         "bulls": None,
    #         "cows": None,
    #         "analysis": None,
    #         "status": None
    #     }
    #     g = GameController()
    #     for _ in range(11):
    #         r = g.guess(0,0,0,0)

    #     r = g._check_game_on(response_object)
    #     self.assertEqual(r, False)
    #     self.assertIn("You already lost! The correct answer was", response_object["status"])

    # def test_gc_check_game_bad_response(self):
    #     g = GameController()
    #     with self.assertRaises(ValueError):
    #         g._check_game_on(response_object=None)

    # def test_gc_check_game_bad_game(self):
    #     g = GameController()
    #     with self.assertRaises(ValueError):
    #         response_object = {
    #             "bulls": None,
    #             "cows": None,
    #             "analysis": None,
    #             "status": None
    #         }
    #         g.game = None
    #         g._check_game_on(response_object=response_object)

    # def test_gc_already_won_game(self):
    #     g = GameController()
    #     ans = g.game.answer.word
    #     r = g.guess(*ans)
    #     self.assertEqual(r["bulls"], 4)
    #     r = g.guess(*ans)
    #     self.assertEqual(r["bulls"], None)

    # def tearDown(self):
    #     pass