from unittest import TestCase
from python_cowbull_server import app
from Routes.V1 import V1
from flask_helpers.ErrorHandler import ErrorHandler
from flask_controllers import GameServerController
from flask_controllers import HealthCheck
from flask_controllers import Readiness
from flask_controllers import GameModes


class TestV1Routes(TestCase):
    def setUp(self):
        self.app = app.test_client()
        error_handler = ErrorHandler()
        v1 = V1(error_handler=error_handler, app=app)
        v1.game(controller=GameServerController)
        v1.modes(controller=GameModes)
        v1.health(controller=HealthCheck)
        v1.readiness(controller=Readiness)

    def test_default_game(self):
        results = self.app.get('/v1/game')
        self.assertTrue(
            "key" in results.data and "served-by" in results.data
        )

    def tearDown(self):
        pass
