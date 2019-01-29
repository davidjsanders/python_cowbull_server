import json
from unittest import TestCase
from flask_controllers import *
from python_cowbull_server import app
from python_cowbull_server.Configurator import Configurator
from Routes.V1 import V1
from flask_helpers.ErrorHandler import ErrorHandler

class TestFlaskControllers(TestCase):
    def setUp(self):
        self.eh = ErrorHandler(
            module="TestFlaskControllers",
        )
        self.app = app.test_client()
        self.application = self.app.application
        c = Configurator()
        if self.application.config["PYTHON_VERSION_MAJOR"] < 3:
            self.json_raises = ValueError
        else:
            self.json_raises = json.JSONDecodeError

    def test_fc_gm_bad_init(self):
        with self.assertRaises(RuntimeError):
            gm = GameModes()
            gm.get()

    def test_fc_gm_init(self):
        v1 = V1(error_handler=self.eh, app=self.app.application)
        v1.modes(controller=GameModes)
        gm = GameModes()
        with self.application.test_request_context('/game'):
            gm.get()
