import json

from unittest import TestCase
from Game.GameController import GameController
from Game.GameMode import GameMode
from python_cowbull_server import app
from python_cowbull_server.Configurator import Configurator

class TestConfigurator(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.c = Configurator()
        if app.config["PYTHON_VERSION_MAJOR"] < 3:
            self.json_raises = ValueError
        else:
            self.json_raises = json.JSONDecodeError

    def tearDown(self):
        self.c = Configurator()
        self.c.execute_load(self.app.application)

    def test_co_init(self):
        c = Configurator()
        self.assertIsInstance(c, Configurator)

    def test_co_execute_load(self):
        self.c.execute_load(self.app.application)

    def test_co_noapp_execute_load(self):
        with self.assertRaises(ValueError):
            self.c.execute_load(None)

    def test_co_badtype_execute_load(self):
        with self.assertRaises(TypeError):
            self.c.execute_load('app')

    def test_co_get_variables(self):
        ret = self.c.get_variables()
        self.assertIsInstance(ret, list)

    def test_co_badtype_get_variables(self):
        with self.assertRaises(TypeError):
            self.c.get_variables('foobar')

    def test_co_badvalue_load_defaults(self):
        with self.assertRaises(ValueError):
            self.c._load_defaults('')

    def test_co_badtype_load_defaults(self):
        with self.assertRaises(TypeError):
            self.c._load_defaults()

    def test_co_badfile_load_defaults(self):
        with self.assertRaises(IOError):
            self.c._load_defaults('foo.bar')

    def test_co_load_variables(self):
        self.c.execute_load(self.app.application)
        self.c.load_variables({"FLASK_PORT":22})
        values_set = self.c.dump_variables()
        test_item = [item for item in values_set if item[0] == "FLASK_PORT"]
        self.assertEqual(len(test_item), 1)
        test_item = test_item[0]
        self.assertEqual(test_item[0], "FLASK_PORT")
        self.assertEqual(test_item[1], 22)

    def test_co_badattr_load_variables(self):
        self.c.execute_load(self.app.application)
        with self.assertRaises(AttributeError):
            self.c.load_variables("FLASK_PORT")
