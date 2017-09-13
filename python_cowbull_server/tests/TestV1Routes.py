import json

from unittest import TestCase
from python_cowbull_server import app
from Routes.V1 import V1
from flask_helpers.ErrorHandler import ErrorHandler
from flask_controllers import GameServerController
from flask_controllers import HealthCheck
from flask_controllers import Readiness
from flask_controllers import GameModes


class TestV1Routes(TestCase):
    @classmethod
    def setUpClass(cls):
        error_handler = ErrorHandler()
        v1 = V1(error_handler=error_handler, app=app)
        v1.game(controller=GameServerController)
        v1.modes(controller=GameModes)
        v1.health(controller=HealthCheck)
        v1.readiness(controller=Readiness)

    @staticmethod
    def _prepare_json_string(value=None):
        if not value:
            return

        if isinstance(value, bytes):
            return value.decode("utf-8")
        else:
            return value

    def _get_test(self, mode=None):
        url = '/v1/game' + ('?mode={}'.format(mode) if mode else '')
        results = self.app.get(url)
        required_keys = set(("key", "served-by"))
        keys_returned_from_url = set(json.loads(self._prepare_json_string(results.data)))
        self.assertTrue(
            required_keys <= keys_returned_from_url
        )
        self.assertTrue(results.status_code == 200)

    def setUp(self):
        self.app = app.test_client()

    def test_v1_game_default(self):
        self._get_test()

    def test_v1_game_all_modes(self):
        results = self.app.get('/v1/modes')
        modes = json.loads(self._prepare_json_string(results.data))
        for mode in modes["modes"]:
            self._get_test(mode=mode["mode"])

    def test_v1_game_post(self):
        url = '/v1/game'
        results = self.app.get(url)
        results_dict = json.loads(self._prepare_json_string(results.data))
        key = results_dict["key"]
        json_data = {
            "key": key,
            "digits": [0, 1, 2, 3]
        }
        json_string = json.dumps(json_data)
        headers = {"Content-type": "application/json"}
        result = self.app.post(
            '/v1/game',
            data=json_string,
            headers=headers
        )
        self.assertTrue(result.status_code == 200)

    def test_v1_game_post_baddigits(self):
        url = '/v1/game'
        results = self.app.get(url)
        results_dict = json.loads(self._prepare_json_string(results.data))
        key = results_dict["key"]
        json_data = {
            "key": key,
            "digits": [0, 1, 2, "S"]
        }
        json_string = json.dumps(json_data)
        headers = {"Content-type": "application/json"}
        result = self.app.post(
            '/v1/game',
            data=json_string,
            headers=headers
        )
        self.assertTrue(result.status_code == 400)

    def test_v1_game_post_badkey(self):
        json_data = {
            "key": "12345678-0123-abcd-1234-0987654321fe",
            "digits": [0, 1, 2, 3]
        }
        json_string = json.dumps(json_data)
        headers = {"Content-type": "application/json"}
        result = self.app.post(
            '/v1/game',
            data=json_string,
            headers=headers
        )
        self.assertTrue(result.status_code == 400)

    def test_v1_get_modes(self):
        results = self.app.get('/v1/modes')
        required_keys = set(("notes", "modes", "default-mode", "instructions"))
        keys_returned_from_url = set(json.loads(self._prepare_json_string(results.data)))
        self.assertTrue(
            required_keys <= keys_returned_from_url
        )
        self.assertTrue(results.status_code == 200)

    def test_v1_get_ready(self):
        results = self.app.get('/v1/ready')
        required_keys = set(("status",))
        keys_returned_from_url = set(json.loads(self._prepare_json_string(results.data)))
        self.assertTrue(
            required_keys <= keys_returned_from_url
        )
        self.assertTrue(results.status_code == 200)

    def test_v1_get_health(self):
        results = self.app.get('/v1/health')
        required_keys = set(("health",))
        keys_returned_from_url = set(json.loads(self._prepare_json_string(results.data)))
        self.assertTrue(
            required_keys <= keys_returned_from_url
        )
        self.assertTrue(results.status_code == 200)

    def tearDown(self):
        pass
