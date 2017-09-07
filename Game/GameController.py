import copy
import json
import logging

from Game.GameObject import GameObject
from Game.GameMode import GameMode

from python_digits import DigitWord


class GameController(object):
    """GameController - Provides the controller functions (load, save, and guess) to
    interact with a CowBull game.
    """
    GAME_PLAYING = "playing"    # The game is in progress.
    GAME_WAITING = "waiting"    # The game is waiting to start - not currently used.
    GAME_WON = "won"            # The game is over and has been won.
    GAME_LOST = "lost"          # The game is over and has been lost.

    def __init__(self, game_json=None, game_modes=None, mode=None):
        """
        Initialize a GameController object to allow the game to be played. The controller
        creates a game object (see GameObject.py) and allows guesses to be made against
        the 'hidden' object.

        :param game_json: <optional>, if provided is a JSON serialized representation
        of a game; if not provided a new game is instantiated.
        :param game_modes: <optional>, a list of GameMode objects representing game modes.
        :param mode: <optional>, the mode the game should be played in; may be a GameMode
        object or a str representing the name of a GameMode object already defined (e.g.
        passed via game_modes).
        """
        # load game_modes
        logging.debug("GameController: __init__: Setup game modes")
        self._game_modes = None
        self.load_modes(input_modes=game_modes)

        # load any game passed
        logging.debug("GameController: __init__: Loading any saved game")
        self.game = None
        self.load(game_json=game_json, mode=mode)

    #
    # Properties
    #

    @property
    def game_modes(self):
        return sorted(self._game_modes, key=lambda x: x.priority)

    @property
    def game_mode_names(self):
        return [game_mode.mode for game_mode in sorted(self._game_modes, key=lambda x: x.priority)]

    #
    # 'public' methods
    #

    def guess(self, *args):
        """
        Make a guess, comparing the hidden object to a set of provided digits. The digits should
        be passed as a set of arguments, e.g:

        * for a normal game: 0, 1, 2, 3
        * for a hex game: 0xA, 0xB, 5, 4
        * alternate for hex game: 'A', 'b', 5, 4

        :param args: An iterable of digits (int or str)
        :return: A dictionary object detailing the analysis and results of the guess
        """

        if self.game is None:
            raise ValueError("The Game is unexpectedly undefined!")

        response_object = {
            "bulls": None,
            "cows": None,
            "analysis": None,
            "status": None
        }

        if self.game.status == self.GAME_WON:
            response_object["status"] = \
                self._start_again_message("You already won!")
        elif self.game.status == self.GAME_LOST:
            response_object["status"] = \
                self._start_again_message("You already lost!")
        elif self.game.guesses_remaining < 1:
            response_object["status"] = \
                self._start_again_message("You've made too many guesses")
        else:
            guess_made = DigitWord(*args, wordtype=self.game.mode.digit_type)
            comparison = self.game.answer.compare(guess_made)

            self.game.guesses_made += 1
            response_object["bulls"] = 0
            response_object["cows"] = 0
            response_object["analysis"] = []

            for comparison_object in comparison:
                if comparison_object.match:
                    response_object["bulls"] += 1
                elif comparison_object.in_word:
                    response_object["cows"] += 1
                response_object["analysis"].append(comparison_object.get_object())

            if response_object["bulls"] == self.game.mode.digits:
                self.game.status = self.GAME_WON
                self.game.guesses_made = self.game.mode.guesses_allowed
                response_object["status"] = self._start_again_message(
                    "Congratulations, you win!"
                )
            elif self.game.guesses_remaining < 1:
                self.game.status = self.GAME_LOST
                response_object["status"] = self._start_again_message(
                    "Sorry, you lost!"
                )

        return response_object

    def load(self, game_json=None, mode=None):
        """
        Load a game from a serialized JSON representation. The game expects a well defined
        structure as follows (Note JSON string format):

        '{
            "guesses_made": int,
            "key": "str:a 4 word",
            "status": "str: one of playing, won, lost",
            "mode": {
                "digits": int,
                "digit_type": DigitWord.DIGIT | DigitWord.HEXDIGIT,
                "mode": GameMode(),
                "priority": int,
                "help_text": str,
                "instruction_text": str,
                "guesses_allowed": int
            },
            "ttl": int,
            "answer": [int|str0, int|str1, ..., int|strN]
        }'

        * "mode" will be cast to a GameMode object
        * "answer" will be cast to a DigitWord object

        :param game_json: The source JSON - MUST be a string
        :param mode: A mode (str or GameMode) for the game being loaded
        :return: A game object
        """

        _mode = mode or 'normal' # Default mode to normal if not provided

        logging.debug("GameController: load: Validating (any) JSON provided")
        if game_json is None:    # New game_json
            logging.debug("GameController: load: No JSON, so start new game.")
            logging.debug("GameController: load: Validating (any) mode provided")
            if mode is not None:
                logging.debug("GameController: load: mode provided, checking if string or GameMode")
                if isinstance(mode, str):
                    logging.debug("GameController: load: Mode is a string; matching name {}".format(mode))
                    _game_object = GameObject(mode=self._match_mode(mode=mode))
                elif isinstance(mode, GameMode):
                    logging.debug("GameController: load: Mode is a GameMode object")
                    _game_object = GameObject(mode=mode)
                else:
                    logging.debug("GameController: load: Mode is invalid")
                    raise TypeError("Game mode must be a GameMode or string")
            else:
                logging.debug("Game mode is None, so default mode used.")
                _game_object = GameObject(mode=self._game_modes[0])
            _game_object.status = self.GAME_PLAYING
        else:
            logging.debug("GameController: load: JSON provided")
            if not isinstance(game_json, str):
                raise TypeError("Game must be passed as a serialized JSON string.")

            logging.debug("GameController: load: Attempting to load")
            game_dict = json.loads(game_json)

            logging.debug("GameController: load: Validating mode exists in JSON")
            if not 'mode' in game_dict:
                raise ValueError("Mode is not provided in JSON; game_json cannot be loaded!")

            _mode = GameMode(**game_dict["mode"])
            _game_object = GameObject(mode=_mode, source_game=game_dict)

        logging.debug("GameController: load: Deep copy loaded (or new) object")
        self.game = copy.deepcopy(_game_object)

    def save(self):
        """
        Save returns a string of the JSON serialized game object.

        :return: str of JSON serialized data
        """

        return json.dumps(self.game.dump())

    def load_modes(self, input_modes=None):
        """
        Loads modes (GameMode objects) to be supported by the game object. Four default
        modes are provided (normal, easy, hard, and hex) but others could be provided
        either by calling load_modes directly or passing a list of GameMode objects to
        the instantiation call.

        :param input_modes: A list of GameMode objects; nb: even if only one new GameMode
        object is provided, it MUST be passed as a list - for example, passing GameMode gm1
        would require passing [gm1] NOT gm1.

        :return: A list of GameMode objects (both defaults and any added).
        """

        # Set default game modes
        _modes = [
            GameMode(
                mode="normal", priority=2, digits=4, digit_type=DigitWord.DIGIT, guesses_allowed=10
            ),
            GameMode(
                mode="easy", priority=1, digits=3, digit_type=DigitWord.DIGIT, guesses_allowed=6
            ),
            GameMode(
                mode="hard", priority=3, digits=6, digit_type=DigitWord.DIGIT, guesses_allowed=6
            ),
            GameMode(
                mode="hex", priority=4, digits=4, digit_type=DigitWord.HEXDIGIT, guesses_allowed=10
            )
        ]

        if input_modes is not None:
            if not isinstance(input_modes, list):
                raise TypeError("Expected list of input_modes")

            for mode in input_modes:
                if not isinstance(mode, GameMode):
                    raise TypeError("Expected list to contain only GameMode objects")
                _modes.append(mode)

        self._game_modes = copy.deepcopy(_modes)

    #
    # 'private' methods
    #
    def _match_mode(self, mode):
        _mode = [game_mode for game_mode in self._game_modes if game_mode.mode == mode]
        if len(_mode) < 1:
            raise ValueError("Mode {} not found - has it been initiated?".format(mode))
        _mode = _mode[0]

        if not _mode:
            raise ValueError("For some reason, the mode is defined but unavailable!")

        return _mode

    def _start_again_message(self, message=None):
        """Simple method to form a start again message and give the answer in readable form."""
        logging.debug("Start again message delivered: {}".format(message))
        the_answer = ', '.join(
            [str(d) for d in self.game.answer][:-1]
        ) + ', and ' + [str(d) for d in self.game.answer][-1]

        return "{0}{1} The correct answer was {2}. Please start a new game.".format(
            message,
            "." if message[-1] not in [".", ",", ";", ":", "!"] else "",
            the_answer
        )
