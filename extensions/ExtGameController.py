from python_cowbull_game.GameController import GameController
from python_cowbull_game.GameMode import GameMode


class ExtGameController(GameController):
    additional_modes = [
        GameMode(mode="SuperTough", priority=6, digits=10, digit_type=0),
        GameMode(mode="hexTough", priority=5, digits=3, guesses_allowed=3, digit_type=1)
    ]

    def __init__(self, game=None):
        super(ExtGameController, self).__init__(game=game)
        self.add_mode(self.additional_modes)
