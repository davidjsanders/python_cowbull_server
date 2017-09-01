from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
from python_cowbull_game.GameObject import GameObject as GameObject


class GameModes(MethodView):
    def get(self):
        game_object = GameObject()

        if request.args.get('textmode', None):
            response_data = game_object.game_modes
        else:
            response_data = [{"mode": game_object.game_types[gt].mode,
                              "digits": game_object.game_types[gt].digits,
                              "guesses": game_object.game_types[gt].guesses
                             } for gt in game_object.game_types]

        return build_response(
            html_status=200,
            response_data=response_data,
            response_mimetype="application/json"
        )
