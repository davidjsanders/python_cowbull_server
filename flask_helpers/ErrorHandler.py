import json
import logging
import os
from flask import Response


class ErrorHandler(object):
    def __init__(self, **kwargs):
        self.defaults = {}
        self.defaults["module"] = kwargs.get("module", None)
        self.defaults["method"] = kwargs.get("method", None)
        self.basicConfig = logging.basicConfig

        str_level = None
        try:
            str_level = kwargs.get("level", None)
            level = int(str_level)
        except (ValueError, TypeError) as exmsg:
            if str_level:
                print("*** INVALID LOGGING_LEVEL: --> {}; is LOGGING_LEVEL set to a number?".format(exmsg))
            level = logging.WARNING

        self.basicConfig(
            level=level,
            format=kwargs.get("format", "%(asctime)s %(levelname)s: %(message)s")
        )

    #
    # Properties
    #
    @property
    def module(self):
        return self.defaults["module"]

    @module.setter
    def module(self, value):
        if not isinstance(value, str):
            raise TypeError("Module must be a string.")
        self.defaults["module"] = value

    @property
    def method(self):
        return self.defaults["method"]

    @method.setter
    def method(self, value):
        if not isinstance(value, str):
            raise TypeError("Method must be a string.")
        self.defaults["method"] = value

    @property
    def logger(self):
        return logging.getLogger()

    #
    # 'public' methods
    #
    def error(self, module=None, method=None, status=None, exception=None, message=None):
        response_dict = {
            "status": status or "NA",
            "module": module or self.defaults["module"],
            "method": method or self.defaults["method"],
            "exception": exception,
            "message": message or "No message was provided!"
        }

        self.log(
            module=response_dict["module"],
            method=response_dict["method"],
            exception=response_dict["exception"],
            status=response_dict["status"],
            message=response_dict["message"],
            logger=logging.error,
            verbose=True
        )

        return Response(
            mimetype="application/json",
            status=response_dict["status"],
            response=json.dumps(response_dict)
        )

    def log(
            self,
            module=None,
            method=None,
            exception=None,
            status=None,
            message=None,
            logger=None,
            verbose=None
    ):
        if logger is None:
            logger = logging.debug
        if verbose is None:
            _verbose = os.getenv("debug_verbose", False) == "true"
        else:
            _verbose = verbose

        if _verbose:
            _message = "{}: {}: STATUS:{} MESSAGE:{} {}".format(
                module or self.defaults["module"],
                method or self.defaults["method"],
                status,
                message,
                "EXCEPTION:{}".format(exception) if exception is not None else ""
            )
        else:
            _message = "{}: {}: {}".format(
                module or self.defaults["module"],
                method or self.defaults["method"],
                message
            )

        logger(_message)
