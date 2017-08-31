# GameController is class based on Flask.MethodView which provides the logic
# required to handle get and post requests. It could also handle put, patch, etc.,
# but currently only supports GET (get a new game) and POST (make a guess against
# an existing game

# Import standard packages
import json
import logging
import socket
import sys
from redis.exceptions import ConnectionError

# Import flask packages
from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
from flask_helpers.ErrorHandler import ErrorHandler
from werkzeug.exceptions import BadRequest

# Import the Game and GameObject.
from python_cowbull_game.Game import Game
from python_cowbull_game.GameObject import GameObject as GameObject

# Import a persistence package
from Persistence.RedisPersist import RedisPersist as PersistenceEngine

# Import the Flask app object
from python_cowbull_server import app


class GameController(MethodView):
    # Initialize class level variables
    handler = None

    def __init__(self):
        # Get an error handler that can be used to handle errors and log to
        # std i/o. The error handler logs the error and forms an HTML response
        # using Flask's Response class.
        self.handler = ErrorHandler(module="GameController", method="__init__")
        self.handler.log(message="Loading configuration from environment.", status=0)

        # Get key configuration information from Flask's configuration engine.
        # These should have all been set before (in python_cowbull_server/__init__.py)
        # and if they haven't (for whatever reason) an exception WILL be raised.
        self.game_version = app.config.get("GAME_VERSION")
        self.redis_host = app.config.get("REDIS_HOST")
        self.redis_port = app.config.get("REDIS_PORT")
        self.redis_db = app.config.get("REDIS_DB")
        self.redis_auth = app.config.get("REDIS_USEAUTH")

        # Log the configuration to the handler.
        self.handler.log(
            message="Redis configured for: {}:{}/{} -- auth? {}"\
                .format(
                    self.redis_host,
                    self.redis_port,
                    self.redis_db,
                    self.redis_auth
                ),
            status=0
        )

    def get(self):
        # Set the error handler to default the module and method so that logging
        # calls can be more precise and easier to read.
        self.handler = ErrorHandler(module="GameController", method="get")
        self.handler.log(message='Processing GET request', status=0)

        # Check if a game mode has been passed as a query parameter. If it has,
        # validate the mode and use it to create the game. If it hasn't, then
        # default to normal.
        game_mode = request.args.get('mode', 'normal')
        game_object = GameObject()

        if game_mode not in game_object.game_modes:
            return self.handler.error(
                status=400, exception="Invalid game mode", message="There is no game mode {}!".format(game_mode)
            )

        # Get a persistence engine. Currently, this is set to be redis but can
        # easily be changed simply by changing the import statement above. Ideally
        # an abstract class would be created which concrete classes could inherit
        # from to ensure uniform consistency in persistence handling regardless
        # of the engine (Redis, Mongo, etc.) used.
        try:
            persister = PersistenceEngine\
                (host=self.redis_host, port=self.redis_port, db=self.redis_db)

            self.handler.log(message='Persister instantiated', status=0)
        except ConnectionError as ce:
            return self.handler.error(status=503, exception=str(ce), message="There is no redis service available!")
        except AttributeError as ae:
            return self.handler.error(status=503, exception=str(ae), message="An internal error occurred - attribute missing for redis - check GameController:__init__")

        # Instantiate a game object. This calls the cowbull game object and creates
        # an empty object.
        _game = Game(game_object=game_object)
        self.handler.log(message='Game object created', status=0)

        #TODO ADD VALIDATION!

        #
        # Create a new game
        #
        jsonstr = _game.new_game(mode=game_mode)
        self.handler.log(message='New game created with key {}'.format(_game.key), status=0)

        #
        # Save the newly created game
        #
        persister.save(_game.key, _game.save_game())
        self.handler.log(message='Game {} persisted.'.format(_game.key), status=0)

        #
        # Build the user response - key, no. of digits, and no. of guesses
        #
        _response = {
            "key": _game.key,
            "digits": _game.digits_required,
            "guesses": _game.guesses_allowed,
            "served-by": socket.gethostname()
        }

        self.handler.log(message='GET request fulfilled. Returned: {}'.format(_response), status=0)

        return build_response(html_status=200, response_data=_response, response_mimetype="application/json")

    def post(self):
        self.handler = ErrorHandler(module="GameController", method="post")
        self.handler.log(message='Processing POST request.', status=0)

        #
        # Get the JSON from the request
        #
        try:
            self.handler.log(message='Attempting to load JSON', status=0)
            json_dict = request.get_json()
            self.handler.log(message='Loaded JSON. Returned: {}'.format(json_dict), status=0)
        except BadRequest as e:
            return self.handler.error(
                status=400,
                exception=e.description,
                message="Bad request. There was no JSON present. ### LIKELY CALLER ERROR ###"
            )

        #
        # Get a persister
        #
        try:
            self.handler.log(message='Getting persister', status=0)
            persister = PersistenceEngine(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        except ConnectionError as ce:
            return self.handler.error(
                status=503,
                exception=str(ce),
                message="There is no redis service available!"
            )

        #
        # Load the game based on the JSON. If the JSON data is invalid, return a
        # response to the user indicating an HTML status, the exception, and an
        # explanatory message.
        #
        try:
            _key = json_dict["key"]
            self.handler.log(message='Attempting to load game {}'.format(_key), status=0)
        except TypeError as te:
            return self.handler.error(
                status=500,
                exception=str(te),
                message="Bad request. For some reason the json_dict is None! Are you "
                        "sure the header is set to application/json?"
            )

        _game = None
        try:
            _game = self._get_game(persister, _key)
            self.handler.log(message='Loaded game {}'.format(_key), status=0)
        except RuntimeError as ve:
            return self.handler.error(
                status=500,
                exception=str(ve),
                message="Bad request. For some reason the json_dict was None!"
            )
        except KeyError as ke:
            return self.handler.error(
                status=400,
                exception=str(ke),
                message="The request must contain a valid game key."
            )
        except TypeError as te:
            return self.handler.error(
                status=400,
                exception=str(te),
                message="The game key provided was invalid."
            )

        #
        # Get the digits being guessed and add them to a list
        #
        try:
            self.handler.log(message='Getting digits from {}'.format(json_dict))
            _guesses = self._get_digits(game=_game, json_dict=json_dict)
            self.handler.log(message='Guesses extracted from JSON: {}'.format(_guesses), status=0)
        except RuntimeError as ve:
            return self.handler.error(
                status=500,
                exception=str(ve),
                message="Bad request. For some reason the json_dict was None!"
            )
        except ValueError as ve:
            return self.handler.error(
                status=400,
                exception=str(ve),
                message="There was a problem with the value of the digits provided!"
            )
        except KeyError as ke:
            return self.handler.error(
                status=400,
                exception=str(ke),
                message="The request must contain an array of digits called 'digits'"
            )
        except TypeError as te:
            return self.handler.error(
                status=400,
                exception=str(te),
                message="The game key provided was invalid."
            )

        #
        # Make a guess
        #
        try:
            self.handler.log(message="In guess")
            self.handler.log(message='Making a guess with digits: {}'.format(_guesses), status=0)
            _analysis = _game.guess(*_guesses)
            self.handler.log(message='Retrieved guess analysis', status=0)
        except ValueError as ve:
            return self.handler.error(
                status=400,
                exception=str(ve),
                message="There is a problem with the digits provided!"
            )

        #
        # Save the game
        #
        self.handler.log(message='Update game (save) after guess', status=0)
        save_game = _game.save_game()
        persister.save(key=_key, jsonstr=save_game)

        #
        # Return the analysis of the guess to the user.
        #
        _display_info = json.loads(save_game)
        del(_display_info["answer"])
        _return_response = \
            {
                "game": _display_info,
                "outcome": _analysis,
                "served-by": socket.gethostname()
            }

        self.handler.log(message='Returning analysis and game info to caller', status=0)
        return build_response(response_data=_return_response)

    @staticmethod
    def _get_digits(game=None, json_dict=None):
        if game is None:
            raise RuntimeError("Game object must be instantiated before loading digits!")

        if json_dict is None:
            raise RuntimeError("Game must be loaded before loading digits!")
        if 'digits' not in json_dict:
            raise KeyError("The JSON provided no digits object!")

        digits_required = game.digits_required

        digits = json_dict["digits"]

        if len(digits) != digits_required:
            raise ValueError("The digits provided did not match the required number ({})".format(digits_required))

        return digits

    @staticmethod
    def _get_game(persister=None, game_key=None):
        if game_key is None:
            raise RuntimeError("The game key must be specified and cannot be None!")
        if persister is None:
            raise RuntimeError("The persistence engine is None!")

        g = Game()

        _json = persister.load(game_key)

        if _json is None:
            raise KeyError("The key provided is invalid.")

        if sys.version_info[0] > 2:
            exception_to_check = json.decoder.JSONDecodeError
        else:
            exception_to_check = ValueError

        try:
            g.load_game(str(_json))
        except exception_to_check as e:
            return None

        return g
