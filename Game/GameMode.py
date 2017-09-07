import logging


class GameMode(object):
    """
    A representation of a game mode (complexity, number of digits, guesses allowed, etc.). The
    mode contains the following information:

    * mode <str>                A text name for the mode.
    * priority <int>            An integer of the priority in terms of returning a list.
    * digits <int>              An integer representing the number of digits used in this mode.
    * digit_type <int>          An integer representing the type of digit used, e.g. Hex or Digit
    * guesses_allowed <int>     An integer representing the number of guesses that can be made
    * instruction_text <str>    A free form string for instructions on the mode
    * help_text <str>           A free form string offering help text for the mode

    """
    def __init__(
            self,
            mode=None,
            priority=None,
            digits=None,
            digit_type=None,
            guesses_allowed=None,
            instruction_text=None,
            help_text=None
    ):
        """
        Constructor to create a new mode.

        :param mode: <str> A text name for the mode.
        :param priority: <int> priority of modes (in terms of returning a list)
        :param digits: <int> number of digits used in this mode.
        :param digit_type: <int> type of digit, e.g. DigitWord.HEXDIGIT or DigitWord.DIGIT
        :param guesses_allowed: <int> Number of guesses permitted.
        :param instruction_text: <str> Instruction text (dependent upon caller to show)
        :param help_text: <str> Help text (dependent upon caller to show)

        """
        # Initialize variables
        self._mode = None
        self._priority = None
        self._digits = None
        self._digit_type = None
        self._guesses_allowed = None
        self._instruction_text = None
        self._help_text = None

        # NOTICE: Properties are used to set 'private' fields (e.g. _mode) to handle
        # data validation in one place. When adding a new parameter to __init__ ensure
        # that the property is created (following the existing code) and set the
        # property not the 'internal' variable.
        #
        self.mode = mode
        self.priority = priority
        self.digits = digits
        self.digit_type = digit_type
        self.guesses_allowed = guesses_allowed
        self.instruction_text = instruction_text
        self.help_text = help_text

    #
    # Overrides
    #
    def __str__(self):
        """
        Override of __str__ method.
        :return: <str> representation of the GameMode
        """
        return str(self.dump())

    def __repr__(self):
        """
        Override of __repr__ method.
        :return: <str> representation of object showing mode name
        """
        return "<GameObject: mode: {}>".format(self._mode)

    #
    # Properties
    #
    @property
    def mode(self):
        """
        The name of the mode.
        :return: <str>
        """
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = self._property_setter(
            keyword="mode", required=True, datatype=str, value=value
        )

    @property
    def priority(self):
        """
        The priority of the mode when collected in a list. For example: priority 10 is less than 20,
        so 10 will come before 20 in a list of GameMode objects.

        This is useful because other modules might return a sorted list of GameMode objects to their
        callers and priority provides a simple means to sort and sequence a collection of GameMode
        objects.

        :return: <int>
        """
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = self._property_setter(
            keyword="priority", required=True, datatype=int, value=value
        )

    @property
    def digits(self):
        """
        The number of digits used by the DigitWord used in this mode; e.g. a value of 3 would
        indicate there are three digits (e.g. 1, 2, and 3), while a value of 5 would indicate
        five values (e.g. 0, 1, 2, 3, 4).

        :return: <int>
        """
        return self._digits

    @digits.setter
    def digits(self, value):
        self._digits = self._property_setter(
            keyword="digits", required=False, default=4, datatype=int, value=value
        )

    @property
    def digit_type(self):
        """
        The digit_type is a flag used to specify the type of digit to be used; for example, a
        digit (DigitWord.DIGIT) enables a single digit between 0 and 9, while a hex digit
        (DigitWord.HEXDIGIT) enables a single digit between 0 and F.

        :return: <int>
        """
        return self._digit_type

    @digit_type.setter
    def digit_type(self, value):
        self._digit_type = self._property_setter(
            keyword="digit_type", required=False, default=0, datatype=int, value=value
        )

    @property
    def guesses_allowed(self):
        """
        The number of guesses the mode is allowed; for example an easy mode might allow
        20 guesses while a hard mode only allowed 7.

        :return: <int>
        """
        return self._guesses_allowed

    @guesses_allowed.setter
    def guesses_allowed(self, value):
        self._guesses_allowed = self._property_setter(
            keyword="guesses_allowed", required=False, default=10, datatype=int, value=value
        )

    @property
    def instruction_text(self):
        """
        Instructions on how to use the mode (if present).
        :return: <str>
        """
        return self._instruction_text

    @instruction_text.setter
    def instruction_text(self, value):
        self._instruction_text = self._property_setter(
            keyword="instruction_text", required=False, datatype=str, value=value
        )

    @property
    def help_text(self):
        """
        Help text intended to guide the user on how to use and interact with the game
        mode.

        :return: <str>
        """
        return self._help_text

    @help_text.setter
    def help_text(self, value):
        self._help_text = self._property_setter(
            keyword="help_text", required=False, datatype=str, value=value
        )

    #
    # 'public' methods
    #
    def dump(self):
        """
        Dump (convert to a dict) the GameMode object
        :return: <dict>
        """
        return {
            "mode": self._mode,
            "priority": self._priority,
            "digits": self._digits,
            "digit_type": self._digit_type,
            "guesses_allowed": self._guesses_allowed,
            "instruction_text": self._instruction_text,
            "help_text": self._help_text
        }

    #
    # 'private' methods
    #
    @staticmethod
    def _property_setter(
            keyword=None,
            required=None,
            default=None,
            datatype=None,
            value=None,
    ):
        _value = value
        logging.debug("_property_setter: Keyword=={} Value=={}".format(keyword, _value))

        if required and not _value and not default:
            raise KeyError("GameMode: '{}' not provided to __init__ and no default provided (or allowed).".format(keyword))

        if not _value and default is not None:
            _value = default

        if _value and not isinstance(_value, datatype):
            raise TypeError("{} is of type {} where {} was expected.".format(keyword, type(_value), datatype))

        logging.debug("_property_setter: Keyword=={} Value=={}".format(keyword, _value))
        return _value
