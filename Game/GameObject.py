import uuid
from python_digits.DigitWord import DigitWord
from Game.GameMode import GameMode


class GameObject(object):
    """
    A GameObject holds the properties (key, status, mode, etc.), states (guesses made, remaining, etc.),
    and the control methods to load, save, or start a new game. There is no game logic in GameObject.py,
    simply the ability to represent a CowBull game.

    See also: GameController --> the control (logic) for the game.

    A GameObject is as follows:

        {
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
        }

    """
    def __init__(
            self,
            mode=None,
            source_game=None
    ):
        """
        Initialize a game object to hold the state, properties, and control of the game.

        :param mode: <required> A GameMode object defining the game play mode.
        :param source_game: <optional> A JSON Serialized representation of the game.
        """

        self._key = None                    # A Unique ID
        self._status = None                 # A representation of status (e.g. won, playing, etc.)
        self._ttl = None                    # Time to live - a representation of time in seconds
        self._answer = None                 # A DigitWord object containing the answer
        self._mode = None                   # A GameMode object containing the mode of the current game
        self._guesses_remaining = None      # How many guesses are remaining -- calculated field
        self._guesses_made = None           # How many guesses have been made

        if source_game:
            # There is a JSON game object, so a game should be loaded. Typically the JSON
            # will have been provided by a persister outside this object, e.g. Redis.
            self.load(source=source_game)
        else:
            # There is no JSON game, so a new game should be created using the mode provided
            # in the instantiation.
            self.new(mode=mode)

    #
    # Properties
    #
    @property
    def key(self):
        return self._key

    @property
    def mode(self):
        return self._mode

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if not isinstance(value, str):
            raise TypeError("Status is expected to be a constant from GameController")
        self._status = value

    @property
    def ttl(self):
        return self._ttl

    @property
    def answer(self):
        return self._answer

    @property
    def guesses_made(self):
        return self._guesses_made

    @guesses_made.setter
    def guesses_made(self, value):
        if not isinstance(value, int):
            raise TypeError("Expected int")
        self._guesses_made = value

    @property
    def guesses_remaining(self):
        return self.mode.guesses_allowed - self._guesses_made

    #
    # 'public' methods
    #
    def dump(self):
        """
        Dump (return) a dict representation of the GameObject. This is a Python
        dict and is NOT serialized. NB: the answer (a DigitWord object) and the
        mode (a GameMode object) are converted to python objects of a list and
        dict respectively.

        :return: python <dict> of the GameObject as detailed above.
        """

        return {
            "key": self._key,
            "status": self._status,
            "ttl": self._ttl,
            "answer": self._answer.word,
            "mode": self._mode.dump(),
            "guesses_made": self._guesses_made
        }

    def load(self, source=None):
        """
        Load the representation of a GameObject from a Python <dict> representing
        the game object.

        :param source: a Python <dict> as detailed above.

        :return:
        """
        if not source:
            raise ValueError("A valid dictionary must be passed as the source_dict")
        if not isinstance(source, dict):
            raise TypeError("A valid dictionary must be passed as the source_dict. {} given.".format(type(source)))

        required_keys = (
            "key",
            "status",
            "ttl",
            "answer",
            "mode",
            "guesses_made")
        if not all(key in source for key in required_keys):
            raise ValueError("The dictionary passed is malformed: {}".format(source))

        _mode = GameMode(**source["mode"])
        self._key = source["key"]
        self._status = source["status"]
        self._ttl = source["ttl"]
        self._answer = DigitWord(*source["answer"], wordtype=_mode.digit_type)
        self._mode = _mode
        self._guesses_made = source["guesses_made"]

    def new(self, mode):
        """
        Create a new instance of a game. Note, a mode MUST be provided and MUST be of
        type GameMode.

        :param mode: <required>

        """

        # If no mode has been defined, then raise an error. The GameController should have
        # passed a mode to the game object, even if it is the default mode.
        if mode is None:
            raise ValueError(
                "A GameMode must be provided to start or load a game object"
            )

        # If the mode has been passed but it's not a GameMode object, throw a TypeError
        # and refuse the object.
        if not isinstance(mode, GameMode):
            raise TypeError(
                "The mode passed to the game is not a GameMode!"
            )

        dw = DigitWord(wordtype=mode.digit_type)
        dw.random(mode.digits)

        self._key = str(uuid.uuid4())
        self._status = ""
        self._ttl = 3600
        self._answer = dw
        self._mode = mode
        self._guesses_remaining = mode.guesses_allowed
        self._guesses_made = 0

    #
    # 'private' methods
    #
