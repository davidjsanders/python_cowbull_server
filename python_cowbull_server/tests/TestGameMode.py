from unittest import TestCase
from Game.GameMode import GameMode


class TestGameMode(TestCase):
    def setUp(self):
        pass

    def test_gm_new(self):
        gm = GameMode(mode="test", priority=1)
        self.assertIsInstance(gm, GameMode)

    def test_gm_new_bad_priority(self):
        with self.assertRaises(KeyError):
            gm = GameMode(mode="test")

    def test_gm_new_no_mode(self):
        with self.assertRaises(KeyError):
            gm = GameMode()

    def test_gm_new_extra_params(self):
        with self.assertRaises(TypeError):
            gm = GameMode(mode="test", priority=3, super_digits="*")

    def test_gm_new_bad_mode(self):
        with self.assertRaises(TypeError):
            gm = GameMode(mode="test", priority=3, digits="S")

    def test_gm_property_priority(self):
        gm = GameMode(mode="test", priority=3)
        gm.priority = 5
        self.assertEqual(gm.priority, 5)

    def test_gm_property_digits(self):
        gm = GameMode(mode="test", priority=3)
        gm.digits = 5
        self.assertEqual(gm.digits, 5)

    def test_gm_property_digit_type(self):
        gm = GameMode(mode="test", priority=3)
        gm.digit_type = 5
        self.assertEqual(gm.digit_type, 5)
