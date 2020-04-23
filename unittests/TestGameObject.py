from unittest import TestCase
from Game.GameObject import GameObject
from Game.GameMode import GameMode
from Game.GameController import GameController
from python_digits.DigitWord import DigitWord


class TestGameObject(TestCase):
    def setUp(self):
        pass

    def test_go_mode_default(self):
        gc = GameController()
        go = GameObject(
            mode=gc.game.mode
        )
        self.assertIsInstance(go, GameObject)

    def test_go_mode_new(self):
        go = GameObject(
            mode=GameMode(mode="testmode", priority=5)
        )
        self.assertIsInstance(go, GameObject)

    def test_go_mode_bad(self):
        with self.assertRaises(TypeError):
            GameObject(
                mode="JustATest"
            )

    def test_go_key(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        self.assertIsInstance(go.key, str)

    def test_go_mode(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        self.assertIsInstance(go.mode, GameMode)

    def test_go_status(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        go.status = "TestStatus"
        self.assertEqual(go.status, "TestStatus")

    def test_go_ttl(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        self.assertIsInstance(go.ttl, int)

    def test_go_answer(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        self.assertIsInstance(go.answer, DigitWord)
        self.assertIsInstance(go.answer.word, list)

    def test_go_guesses_made(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        self.assertEqual(go.guesses_made, 0)

    def test_go_guesses_made_update(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        go.guesses_made += 1
        self.assertEqual(go.guesses_made, 1)

    def test_go_guesses_made_updatebad(self):
        go = GameObject(mode=GameMode(mode="test", priority=5))
        with self.assertRaises(TypeError):
            go.guesses_made = "W1"

    def test_go_guesses_remaining(self):
        go = GameObject(mode=GameMode(mode="Normal", priority=5))
        self.assertEqual(go.guesses_remaining, 10)

    def test_go_dump(self):
        go = GameObject(mode=GameMode(mode="Normal", priority=5))
        test_dict = go.dump()
        self.assertIsInstance(test_dict, dict)
        required_keys = {"key", "status", "ttl", "answer", "mode", "guesses_made"}
        keys_from_dump = set([key for key in go.dump().keys()])
        self.assertTrue(
            required_keys <= keys_from_dump
        )

    def test_go_load(self):
        go = GameObject(mode=GameMode(mode="Normal", priority=5))
        test_dict = go.dump()
        key = test_dict["key"]

        go = GameObject(mode=GameMode(mode="Normal", priority=5))
        self.assertNotEqual(go.key, key)

        go.load(test_dict)
        self.assertEqual(go.key, key)

    def test_go_load_bad(self):
        go = GameObject(mode=GameMode(mode="Normal", priority=5))
        with self.assertRaises(ValueError):
            go.load(
                source={
                    "key": "fred"
                }
            )

    def test_go_new(self):
        go = GameObject(mode=GameMode(mode="Normal", priority=5))
        test_dict = go.dump()
        key = test_dict["key"]

        go.new(mode=GameMode(mode="Normal", priority=5))
        self.assertNotEqual(go.key, key)

    def tearDown(self):
        pass
