import json
import logging
import os
from redis.exceptions import ConnectionError
from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
from werkzeug.exceptions import BadRequest
from python_cowbull_game.Game import Game
from Persistence.RedisPersist import RedisPersist as PersistenceEngine
from flask_helpers.ErrorHandler import ErrorHandler


class GameController(MethodView):
    redis_host = None
    redis_port = 6379
    redis_db = 0

    @staticmethod
    def _dolog(module=None, method=None, message=None, level=None):
        log_string = (module or "GameController")
        log_string += ":" + (method or "not-specified")
        log_string += ">> " + (message or "Not provided?!?")
        if level is None or not isinstance(level, str):
            logging.debug(log_string)
        elif level.lower() == "error":
            logging.error("** "+log_string+" **")
        elif level.lower() == "warning":
            logging.warning(log_string)
        elif level.lower() == "info":
            logging.info(log_string)
        else:
            logging.debug(log_string)

    @staticmethod
    def _return_error(module, method, status, exception, message):
        GameController._dolog(
            module=module,
            method=method,
            message=message,
            level="error"
        )
        _response = {
            "status": status,
            "exception": exception,
            "module": module,
            "method": method,
            "message": message
        }
        return build_response(
            html_status=400,
            response_data=_response,
            response_mimetype="application/json"
        )

    def __init__(self):
        self._dolog(method='__init__', message='Loading environment variables')
        self.redis_host = os.getenv("redis_host", "localhost")
        self.redis_port = os.getenv("redis_port", 6379)
        self.redis_db = os.getenv("redis_db", 0)
        self._dolog(method='__init__', message='DONE')

    def get(self):
        errorHandler = ErrorHandler(module="GameController", method="get")
        errorHandler.error(
            module="GameController",
            method="GET",
            message="This is a test error v2!",
            status=400,
            exception="This is the exception text"
        )
        errorHandler.log(message='Processing GET request')

        try:
            persister = PersistenceEngine(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db
            )
            self._dolog(method='get', message='Persister initiated')
        except ConnectionError as ce:
            return self._return_error(
                module="GameController",
                method='get',
                status=503,
                exception=str(ce),
                message="There is no redis service available!"
            )
        except AttributeError as ae:
            return self._return_error(
                module="GameController",
                method='get',
                status=503,
                exception=str(ae),
                message="An internal error occurred - attribute missing for redis - check GameController:__init__")

        _game = Game()
        self._dolog(method='get', message='Instantiated Game object')

        jsonstr = _game.new_game(mode="normal")
        self._dolog(method='get', message='Created new game: {}'.format(_game.save_game()))

        persister.save(_game.key, _game.save_game())
        self._dolog(method='get', message='Persisted game')

        _response = {
            "key": _game.key,
            "digits": _game.digits_required,
            "guesses": _game.guesses_allowed
        }
        self._dolog(method='get', message='Responding to user with: {}'.format(_response))

        self._dolog(method='get', message='GET request fulfilled.')
        return build_response(
            html_status=200,
            response_data=_response,
            response_mimetype="application/json"
        )

    def post(self):
        self._dolog(method='post', message='Processing POST request')
        #
        # Get the JSON from the request
        #
        try:
            self._dolog(method='post', message='Attempting to load JSON')
            json_dict = request.get_json()
        except BadRequest as e:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=e.description,
                message="Bad request. There was no JSON present. ### LIKELY CALLER ERROR ###"
            )

        #
        # Get a persister
        #
        try:
            self._dolog(method='post', message='Getting a Persister')
            persister = PersistenceEngine(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db
            )
        except ConnectionError as ce:
            return self._return_error(
                module="GameController",
                method='post',
                status=503,
                exception=str(ce),
                message="There is no redis service available!"
            )

        #
        # Load the game based on the JSON. If the JSON data is invalid, return a
        # response to the user indicating an HTML status, the exception, and an
        # explanatory message.
        #
        _key = json_dict["key"]
        self._dolog(method='post', message='Game key is {}'.format(_key))

        _game = None
        try:
            self._dolog(method='post', message='Getting the game in progress')
            _game = self._get_game(persister, _key)
        except RuntimeError as ve:
            return self._return_error(
                module="GameController",
                method='post',
                status=500,
                exception=str(ve),
                message="Bad request. For some reason the json_dict was None!"
            )
        except KeyError as ke:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=str(ke),
                message="The request must contain a valid game key."
            )
        except TypeError as te:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=str(te),
                message="The game key provided was invalid."
            )

        #
        # Get the digits being guessed and add them to a list
        #
        try:
            self._dolog(method='post', message='Making a guess against the game object.')
            _guesses = self._get_digits(game=_game, json_dict=json_dict)
        except RuntimeError as ve:
            return self._return_error(
                module="GameController",
                method='post',
                status=500,
                exception=str(ve),
                message="Bad request. For some reason the json_dict was None!"
            )
        except ValueError as ve:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=str(ve),
                message="There was a problem with the value of the digits provided!"
            )
        except KeyError as ke:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=str(ke),
                message="The request must contain an array of digits called 'digits'"
            )
        except TypeError as te:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=str(te),
                message="The game key provided was invalid."
            )

        #
        # Make a guess
        #
        try:
            self._dolog(method='post', message='Getting the guess analysis to return to the caller')
            _analysis = _game.guess(*_guesses)
        except ValueError as ve:
            return self._return_error(
                module="GameController",
                method='post',
                status=400,
                exception=str(ve),
                message="There is a problem with the digits provided!"
            )

        #
        # Save the game
        #
        self._dolog(method='post', message='Saving the game progress')
        save_game = _game.save_game()
        persister.save(key=_key, jsonstr=save_game)

        #
        # Return the analysis of the guess to the user.
        #
        self._dolog(method='post', message='Returning info to caller.')

        _display_info = json.loads(save_game)
        del(_display_info["answer"])
        _return_response = \
            {
                "game": _display_info,
                "outcome": _analysis
            }

        self._dolog(method='post', message='Returning to caller. POST request complete.')
        return build_response(response_data=_return_response)

    @staticmethod
    def _get_digits(game=None, json_dict=None):
        GameController._dolog(
            method='_get_digits',
            message='Getting the digits from JSON data'
        )
        if game is None:
            raise RuntimeError("Game object must be instantiated before loading digits!")
        if json_dict is None:
            raise RuntimeError("Game must be loaded before loading digits!")
        if 'digits' not in json_dict:
            raise KeyError("The JSON provided no digits object!")

        digits_required = game.digits_required

        digits = json_dict["digits"]

        GameController._dolog(method='post', message='Comparing digit lengths')
        if len(digits) != digits_required:
            raise ValueError("The digits provided did not match the required number ({})".format(digits_required))

        GameController._dolog(method='post', message='Return digits from JSON data')
        return digits

    @staticmethod
    def _get_game(persister=None, game_key=None):
        GameController._dolog(method='_get_game', message='Getting the game in progress')
        if game_key is None:
            raise RuntimeError("The game key must be specified and cannot be None!")
        if persister is None:
            raise RuntimeError("The persistence engine is None!")

        g = Game()

        _json = persister.load(game_key)
        logging.debug("_json is {}".format(_json))

        if _json is None:
            raise KeyError("The key provided is invalid.")

        g.load_game(_json)
        return g
