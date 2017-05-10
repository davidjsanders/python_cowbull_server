from flask.views import MethodView
from flask_helpers.build_response import build_response
from flask_helpers.ErrorHandler import ErrorHandler
from python_cowbull_game.GameObject import GameObject


class GameModes(MethodView):
    def get(self):
        digits = GameObject.digits_used
        guesses = GameObject.guesses_allowed
        game_modes = [mode for mode in GameObject.digits_used]

        return_list = []
        for mode in game_modes:
            return_list.append(
                {
                    "mode": mode,
                    "digits": digits[mode],
                    "guesses": guesses[mode]
                }
            )

        return build_response(
            html_status=200,
            response_data=return_list,
            response_mimetype="application/json"
        )
