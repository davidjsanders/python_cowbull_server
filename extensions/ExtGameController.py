from python_cowbull_game.GameController import GameController
from python_cowbull_game.GameMode import GameMode


class ExtGameController(GameController):
    """
    TBC
    """

    #
    # Example of defining additional game modes:
    # ==========================================
    #
    # Replace:
    # ------------------------------------------
    # additional_modes = []
    #
    # With:
    # ------------------------------------------
    # additional_modes = [
    #    GameMode(mode="SuperTough", priority=6, digits=10, digit_type=0),
    #    GameMode(mode="hexTough", priority=5, digits=3, guesses_allowed=3, digit_type=1)
    # ]
    #

    additional_modes = [
        GameMode(
            mode="hexTough",
            priority=5,
            digits=3,
            guesses_allowed=3,
            digit_type=1,
            help_text="Guess a set of 3 digits between 0 and F",
            instruction_text="hexTough is a hard hexidecimal based game. You need to "
                             "guess 3 digits, each of which needs to be a hex number "
                             "(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, or F). "
                             "The numbers can be passed as hex (0x0, 0xd, 0xE) or as "
                             "strings (A, b, C, 0, 5, etc.)."
        )
    ]

    def __init__(self, game_modes=None, mode=None, game_json=None):
        if game_modes is not None and not isinstance(game_modes, list):
            raise TypeError("ExtGameController expected a list of GameMode objects")

        super(ExtGameController, self).__init__(
            game_json=game_json,
            mode=mode,
            game_modes=self.additional_modes + (game_modes or [])
        )
