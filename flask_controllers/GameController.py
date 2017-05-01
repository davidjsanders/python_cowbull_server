import json
import copy
from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
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