import json
import copy
import logging
from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
from werkzeug.exceptions import BadRequest
from python_cowbull_game.Game import Game
from Persistence.RedisPersist import RedisPersist


class GameController(MethodView):
    def get(self):
        p = RedisPersist()

        g = Game()
        jsonstr = g.new_game()
        game_info = json.loads(jsonstr)

        display_info = copy.deepcopy(game_info)
        del(display_info["answer"])

        p.save(game_info["key"], jsonstr)

        _response = {"Game": display_info}

        return build_response(
            html_status=200,
            response_data=_response,
            response_mimetype="application/json"
        )

    def post(self):
        #
        # Get the JSON from the request
        #
        try:
            json_dict = request.get_json()
        except BadRequest as e:
            return self._return_error(400, e.description, "Bad request. There was no JSON present.")

        #
        # Load the game based on the JSON. If the JSON data is invalid, return a
        # response to the user indicating an HTML status, the exception, and an
        # explanatory message.
        #
        _key = json_dict["key"]
        _game = None
        try:
            _game = self._get_game(json_dict)
        except ValueError as ve:
            return self._return_error(500, str(ve), "Bad request. For some reason the json_dict was None!")
        except KeyError as ke:
            return self._return_error(400, str(ke), "The request must contain a valid game key.")
        except TypeError as te:
            return self._return_error(400, str(te), "The game key provided was invalid.")

        #
        # Get the digits being guessed and add them to a list
        #
        _guesses = [1, 2, 3, 4]

        #
        # Make a guess
        #
        _analysis = _game.guess(*_guesses)

        #
        # Analyse the guess - won, lost, still playing
        #

        #
        # Save the game
        #
        p = RedisPersist()
        p.save(key=_key, jsonstr=_game.save_game())

        #
        # Return the analysis of the guess to the user.
        #
        logging.debug('_game object loaded: {}'.format(_game.save_game()))

        _display_info = json.loads(_game.save_game())
        del(_display_info["answer"])
        _return_response = {"Game": _display_info, "Analysis": _analysis}

        return build_response(response_data=_return_response)

    @staticmethod
    def _return_error(status, exception, message):
        _response = {
            "status": status,
            "exception": exception,
            "message": message
        }
        return build_response(
            html_status=400,
            response_data=_response,
            response_mimetype="application/json"
        )

    @staticmethod
    def _get_game(game_dict=None):
        if game_dict is None:
            raise ValueError("The game dictionary (game_dict) was None!")
        if 'key' not in game_dict:
            raise KeyError("No game key was provided.")

        p = RedisPersist()
        g = Game()

        _json = p.load(game_dict["key"])
        logging.debug("_json is {}".format(_json))

        if _json is None:
            raise KeyError("The key provided is invalid.")

        g.load_game(_json)
        return g

    def oldpost(self):
        control_object = None

        try:
            control_object = request.json
            if control_object is None:
                raise ValueError()
        except Exception as e:
            _response = {
                "status": "error",
                "exception": repr(e),
                "message": "There was no JSON data provided!"
            }
            return build_response(
                html_status=400,
                response_data=_response,
                response_mimetype="application/json"
            )

        key = None
        try:
            print('Control object --> {}'.format(control_object))
            key = control_object.get("key", None)
            if key is None:
                raise KeyError()
        except KeyError as ke:
            _response = {
                "status": "error",
                "exception": repr(ke),
                "message": "There was no key provided in the JSON data!"
            }
            return build_response(
                html_status=400,
                response_data=_response,
                response_mimetype="application/json"
            )

        p = RedisPersist()
        game_data = p.load(key)
        g = Game()
        g.load_game(game_data)
        g.guess(1, 2, 3, 4)
        save = g.save_game()
        p.save(key, save)

        return build_response(
            html_status=200,
            response_data=g.save_game()
        )