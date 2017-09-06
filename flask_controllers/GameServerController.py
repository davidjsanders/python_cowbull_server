# GameController is class based on Flask.MethodView which provides the logic
# required to handle get and post requests. It could also handle put, patch, etc.,
# but currently only supports GET (get a new game) and POST (make a guess against
# an existing game

# Import standard packages
import json
import socket
from redis.exceptions import ConnectionError

# Import flask packages
from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
from flask_helpers.ErrorHandler import ErrorHandler
from werkzeug.exceptions import BadRequest

# Import the Game Controller; NB: a subclassed GameController is imported
# from extensions.ExtGameController which allows specific actions (such as
# additional modes) to be added to the game by default.
#
from extensions.ExtGameController import ExtGameController as GameController

# Import a persistence package
from Persistence.RedisPersist import RedisPersist as PersistenceEngine

# Import the Flask app object
from python_cowbull_server import app


class GameServerController(MethodView):
    """
    tbc
    """

    def __init__(self):
        """
        TBC
        """

        #
        # Get an error handler that can be used to handle errors and log to
        # std i/o. The error handler logs the error and forms an HTML response
        # using Flask's Response class.
        #
        self.handler = ErrorHandler(module="GameServerController", method="__init__")
        self.handler.log(message="Loading configuration from environment.", status=0)

        #
        # Get key configuration information from Flask's configuration engine.
        # These should have all been set before (in python_cowbull_server/__init__.py)
        # and if they haven't (for whatever reason) an exception WILL be raised.
        #
        self.game_version = app.config.get("GAME_VERSION")
        self.redis_host = app.config.get("REDIS_HOST")
        self.redis_port = app.config.get("REDIS_PORT")
        self.redis_db = app.config.get("REDIS_DB")
        self.redis_auth = app.config.get("REDIS_USEAUTH")

        #
        # Log the configuration to the handler.
        #
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
        """
        TBC
        :return:
        """

        #
        # Set the error handler to default the module and method so that logging
        # calls can be more precise and easier to read.
        #
        self.handler = ErrorHandler(module="GameServerController", method="get")
        self.handler.log(message='Processing GET request', status=0)

        #
        # Check if a game mode has been passed as a query parameter. If it has,
        # use it to create the game. If it hasn't, then let the game decide.
        #
        game_mode = request.args.get('mode', None)

        try:
            self.handler.log(message="Creating game with mode {} ({})".format(game_mode, type(game_mode)))
            game_controller = GameController(mode=str(game_mode))
            self.handler.log(message='New game created with key {}'.format(game_controller.game.key), status=0)
        except ValueError as ve:
            return self.handler.error(
                status=400,
                exception="Invalid game mode",
                message="{}: game mode {}!".format(str(ve), game_mode)
            )

        # Get a persistence engine. Currently, this is set to be redis but can
        # easily be changed simply by changing the import statement above. Ideally
        # an abstract class would be created which concrete classes could inherit
        # from to ensure uniform consistency in persistence handling regardless
        # of the engine (Redis, Mongo, etc.) used.
        try:
            persister = PersistenceEngine(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db
            )
            self.handler.log(message='Persister instantiated', status=0)
        except ConnectionError as ce:
            return self.handler.error(status=503, exception=str(ce), message="There is no redis service available!")
        except AttributeError as ae:
            return self.handler.error(status=503, exception=str(ae), message="An internal error occurred - attribute missing for redis - check GameServerController:__init__")

        #
        # Save the newly created game to the persistence engine
        #
        persister.save(game_controller.game.key, game_controller.save())
        self.handler.log(message='Game {} persisted.'.format(game_controller.game.key), status=0)

        #
        # Build the user response - key, no. of digits, and no. of guesses
        #
        _response = {
            "key": game_controller.game.key,
            "mode": game_controller.game.mode.mode,
            "digits": game_controller.game.mode.digits,
            "digit-type": game_controller.game.mode.digit_type,
            "guesses": game_controller.game.mode.guesses_allowed,
            "served-by": socket.gethostname(),
            "help-text": game_controller.game.mode.help_text,
            "instruction-text": game_controller.game.mode.instruction_text
        }

        self.handler.log(message='GET request fulfilled. Returned: {}'.format(_response), status=0)

        return build_response(
            html_status=200,
            response_data=_response,
            response_mimetype="application/json"
        )

    def post(self):
        """
        TBC
        :return:
        """

        self.handler = ErrorHandler(module="GameServerController", method="post")
        self.handler.log(message='Processing POST request.', status=0)

        #
        # Get the JSON from the POST request. If there is no JSON then an exception
        # is raised. IMPORTANT NOTE: When debugging ensuring the Content-type is
        # set to application/json - for example (using cURL):
        #
        # curl -H "Content-type: application/json" ...
        #
        try:
            self.handler.log(message='Attempting to load JSON', status=0)
            json_dict = request.get_json()
            self.handler.log(message='Loaded JSON. Returned: {}'.format(json_dict), status=0)
        except BadRequest as e:
            return self.handler.error(
                status=400,
                exception=e.description,
                message="Bad request. There was no JSON present. Are you sure the "
                        "header Content-type is set to application/json?"
            )

        #
        # Get a persister to enable the game to be loaded and then saved (updated).
        # See the GET method above for more information on the persister.
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
        # Get the game key from the JSON provided above. If it does not exist,
        # return a 400 status (client) error
        #
        try:
            _key = json_dict["key"]
            self.handler.log(message='Attempting to load game {}'.format(_key), status=0)
        except TypeError as te:
            return self.handler.error(
                status=400,
                exception=str(te),
                message="Bad request. For some reason the json_dict is None! Are you "
                        "sure the header is set to application/json?"
            )

        #
        # Load the game based on the key contained in the JSON provided to
        # the POST request. If the JSON data is invalid, return a
        # response to the user indicating an HTML status, the exception, and an
        # explanatory message. If the data
        #
        try:
            _persisted_response = persister.load(key=_key)
            if not _persisted_response:
                raise KeyError(
                    "The game key ({}) was not found in the persistence engine!".format(_key)
                )
            self.handler.log(message="Persister response: {}".format(_persisted_response))

            _loaded_game = json.loads(_persisted_response)
            self.handler.log(message="Loaded game: {}".format(_loaded_game))
        except KeyError as ke:
            return self.handler.error(
                status=400,
                exception=str(ke),
                message="The request must contain a valid game key."
            )

        #
        # Load the game based on the key contained in the JSON provided to
        # the POST request. If the JSON data is invalid, return a
        # response to the user indicating an HTML status, the exception, and an
        # explanatory message. If the data
        #
        try:
            self.handler.log(message="Loading game mode from: {}.".format(_loaded_game["mode"]))
            _mode = _loaded_game["mode"]
            self.handler.log(message="Loaded game mode.")

            _game = GameController(
                game_json=json.dumps(_loaded_game),
                mode=_mode["mode"]
            )
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
        except Exception as e:
            return self.handler.error(
                status=500,
                exception=repr(e),
                message="Exception occurred while loading game!"
            )

        #
        # Get the digits being guessed and add them to a list
        #
        try:
            self.handler.log(message='Getting digits from {}'.format(json_dict))
            _guesses = json_dict["digits"]
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
        save_game = _game.save()
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
