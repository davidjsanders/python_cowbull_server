from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response
from flask_helpers.ErrorHandler import ErrorHandler
# Import the GameObject. The GameObject can come
# from the package, or can be inherited and modified.
#
# Step 1, import the game object.
#
# 1a - a subclassed version of the game object
#from Game.GameObject import GameObject # Note: subclassed
#
# 1b - the original
from python_cowbull_game.GameObject import GameObject as GameObject


class GameModes(MethodView):
    def get(self):
        textonly = request.args.get('textmode', None)
        if textonly:
            return build_response(
                html_status=200,
                response_data=GameObject.game_modes,
                response_mimetype="application/json"
            )

        digits = GameObject.digits_used
        guesses = GameObject.guesses_allowed
        game_modes = GameObject.game_modes
#        game_modes = [mode for mode in GameObject.digits_used]

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
