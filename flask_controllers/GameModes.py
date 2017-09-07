from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response

# Import the Game Controller; NB: a subclassed GameController is imported
# from extensions.ExtGameController which allows specific actions (such as
# additional modes) to be added to the game by default.
#
from extensions.ExtGameController import ExtGameController as GameController


class GameModes(MethodView):
    def get(self):
        game_object = GameController(mode=None)

        if request.args.get('textmode', None):
            response_data = game_object.game_mode_names
        else:
            response_data = [{"mode": gt.mode,
                              "digits": gt.digits,
                              "digit-type": gt.digit_type,
                              "guesses": gt.guesses_allowed
                             } for gt in game_object.game_modes]

        return build_response(
            html_status=200,
            response_data=response_data,
            response_mimetype="application/json"
        )
