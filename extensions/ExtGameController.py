from python_cowbull_game.GameController import GameController
from python_cowbull_game.GameMode import GameMode


class ExtGameController(GameController):
    additional_modes = [
        GameMode(mode="SuperTough", priority=6, digits=10, digit_type=0),
        GameMode(mode="hexTough", priority=5, digits=3, guesses_allowed=3, digit_type=1)
    ]

    def __init__(self, game_modes=None, mode=None, game_json=None):
        if game_modes is not None and not isinstance(game_modes, list):
            raise TypeError("ExtGameController expected a list of GameMode objects")

        super(ExtGameController, self).__init__(
            game_json=game_json,
            mode=mode,
            game_modes=self.additional_modes + (game_modes or [])
        )
