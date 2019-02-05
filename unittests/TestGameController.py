import json

from unittest import TestCase
from Game.GameController import GameController
from Game.GameMode import GameMode
from python_cowbull_server import app
from flask_helpers.VersionHelpers import VersionHelpers

class TestGameController(TestCase):
    def setUp(self):
        self.info = VersionHelpers()
        if self.info.major < 3:
            self.json_raises = ValueError
        else:
            self.json_raises = json.JSONDecodeError

    def test_gc_new(self):
        g = GameController()
        self.assertIsInstance(g, GameController)

    def test_gc_new_badmode(self):
        with self.assertRaises(ValueError):
            GameController(mode="foobar")

    def test_gc_new_game_modes(self):
        mode_list = [
            GameMode(
                mode="test1",
                priority=5,
            ),
            GameMode(
                mode="test2",
                priority=6,
            )
        ]
        g = GameController(game_modes=mode_list)
        modes = g.game_mode_names
        self.assertTrue("test1" in modes)
        self.assertTrue("test2" in modes)
        self.assertFalse("test3" in modes)

    def test_gc_load_game_modes(self):
        mode_list = [
            GameMode(
                mode="test1",
                priority=5,
            ),
            GameMode(
                mode="test2",
                priority=6,
            )
        ]
        g = GameController()
        g.load_modes(input_modes=mode_list)
        modes = g.game_mode_names
        self.assertTrue("test1" in modes)
        self.assertTrue("test2" in modes)

    def test_gc_load_game_modes_nolist(self):
        mode_list = \
            GameMode(
                mode="test1",
                priority=5,
            )
        g = GameController()
        with self.assertRaises(TypeError):
            g.load_modes(input_modes=mode_list)

    def test_gc_load_game_modes_badlist(self):
        mode_list = ["normal", "hard"]
        g = GameController()
        with self.assertRaises(TypeError):
            g.load_modes(input_modes=mode_list)

    def test_gc_new_game_json_normal(self):
        json_string = '{' \
                          '"answer": [9, 6, 9, 4], ' \
                          '"guesses_made": 0, "ttl": 3600, ' \
                          '"status": "playing", ' \
                          '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
                          '"mode": ' \
                            '{"help_text": ' \
                                '"This is the normal (default) game. You need to guess 4 ' \
                                'digits in the right place and each digit must be a whole ' \
                                'number between 0 and 9. There are 10 tries to guess the ' \
                                'correct answer.", ' \
                            '"guesses_allowed": 10, ' \
                            '"instruction_text": ' \
                                '"Enter 4 digits, each digit between 0 and 9 (0, 1, 2, 3, 4, ' \
                                '5, 6, 7, 8, and 9).", ' \
                            '"digit_type": 0, ' \
                            '"priority": 2, ' \
                            '"digits": 4, ' \
                            '"mode": "Normal"}' \
                      '}'
        g = GameController(game_json=json_string, mode="Normal")
        self.assertEqual(g.game.key, "12345678-0123-abcd-1234-0987654321fe")
        self.assertEqual(g.game.guesses_remaining, 10)
        self.assertEqual(g.game.guesses_made, 0)
        self.assertEqual(g.game.answer.word, [9, 6, 9, 4])

    def test_gc_new_game_json_test1(self):
        json_string = '{' \
                        '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
                        '"answer": [4, 2, 0, 0], ' \
                        '"mode": {' \
                            '"guesses_allowed": 2, ' \
                            '"digit_type": 0, ' \
                            '"priority": 5, ' \
                            '"mode": "test1", ' \
                            '"instruction_text": "None", ' \
                            '"help_text": "None", ' \
                            '"digits": 4' \
                        '}, ' \
                        '"guesses_made": 0, ' \
                        '"ttl": 3600, ' \
                        '"status": "playing"' \
                      '}'
        g = GameController(game_json=json_string)
        self.assertEqual(g.game.key, "12345678-0123-abcd-1234-0987654321fe")
        self.assertEqual(g.game.guesses_remaining, 2)
        self.assertEqual(g.game.guesses_made, 0)
        self.assertEqual(g.game.answer.word, [4, 2, 0, 0])

    def test_gc_load(self):
        g = GameController()
        g2 = GameController()
        g2.load(g.save())
        self.assertEqual(g.save(), g2.save())

    def test_gc_load_bad_json(self):
        json_string = ''
        with self.assertRaises(self.json_raises):
            GameController(game_json=json_string)

    def test_gc_load_bad_data(self):
        json_string = '{' \
                        '"key": "12345678-0123-abcd-1234-0987654321fe", ' \
                        '"answer": [4, 0], ' \
                        '"mode": {' \
                            '"guesses_allowed": 2, ' \
                            '"digit_type": 0, ' \
                            '"priority": 5, ' \
                            '"mode": "test1", ' \
                            '"instruction_text": "None", ' \
                            '"help_text": "None", ' \
                            '"digits": 4' \
                        '}, ' \
                        '"guesses_made": 0, ' \
                        '"ttl": 3600, ' \
                        '"status": "playing"' \
                      '}'
        with self.assertRaises(ValueError):
            GameController(game_json=json_string)

    def test_gc_mode_names(self):
        g = GameController()
        modes = g.game_mode_names
        self.assertIsInstance(modes,list)

    def test_gc_guess_once(self):
        g = GameController()
        r = g.guess(0,0,0,0)
        bulls = r.get("bulls", None)
        self.assertIsNot(bulls, None)

    def test_gc_guess_win_game(self):
        g = GameController()
        ans = g.game.answer.word
        r = g.guess(*ans)
        self.assertEqual(r["bulls"], 4)

    def test_gc_guess_lose_game(self):
        g = GameController()
        for i in range(10):
            g.guess(0,0,0,0)
        r = g.guess(0,0,0,0)
        self.assertIsNone(r.get("bulls"))

    def test_gc_guess_no_game(self):
        g = GameController()
        g.game = None
        with self.assertRaises(ValueError):
            g.guess(1,2,3,4)

    def test_gc_check_game_nomore_turns(self):
        response_object = {
            "bulls": None,
            "cows": None,
            "analysis": None,
            "status": None
        }
        g = GameController()
        for _ in range(11):
            r = g.guess(0,0,0,0)

        r = g._check_game_on(response_object)
        self.assertEqual(r, False)
        self.assertIn("You already lost! The correct answer was", response_object["status"])

    def test_gc_check_game_bad_response(self):
        g = GameController()
        with self.assertRaises(ValueError):
            g._check_game_on(response_object=None)

    def test_gc_check_game_bad_game(self):
        g = GameController()
        with self.assertRaises(ValueError):
            response_object = {
                "bulls": None,
                "cows": None,
                "analysis": None,
                "status": None
            }
            g.game = None
            g._check_game_on(response_object=response_object)

    def test_gc_already_won_game(self):
        g = GameController()
        ans = g.game.answer.word
        r = g.guess(*ans)
        self.assertEqual(r["bulls"], 4)
        r = g.guess(*ans)
        self.assertEqual(r["bulls"], None)

    def tearDown(self):
        pass