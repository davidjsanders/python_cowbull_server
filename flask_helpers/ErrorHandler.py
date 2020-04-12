import json
import logging
import os
from flask import Response
from flask_helpers.check_kwargs import check_kwargs


class ErrorHandler(object):
    def __init__(self, **kwargs):
        self.defaults = {}
        self.module = kwargs.get("module", "None")
        self.method = kwargs.get("method", "None")
        self.basic_config = logging.basicConfig

        str_level = None
        caller    = kwargs.get("caller", None)

        try:
            str_level = kwargs.get("level", None)
            level = int(str_level)
        except (ValueError, TypeError) as exmsg:
            level = logging.INFO
            if str_level:
                print("*** NO LOGGING; BEGIN PRINT BLOCK...")
                print("    Issue in ErrorHandler")
                print("    Logging level passed as {}".format(str_level))
                print("    Defaulting logging level to {}".format(level))
                print("*** NO LOGGING; END PRINT BLOCK")
                print("")
        finally:
            self.basic_config(
                level=level,
                format=kwargs.get("format", "%(asctime)s %(levelname)s: %(message)s")
            )
            logging.getLogger().setLevel(level)


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
    def error(
        self, 
        **kwargs
    ):
        check_kwargs(
            parameter_list = ["module", "method", "exception", "status", "message", "logger", "verbose"],
            caller="ErrorHandler-log",
            **kwargs
        )

        module=kwargs.get("module", None)
        method=kwargs.get("method", None)
        status=kwargs.get("status", None)
        exception=kwargs.get("exception", None)
        message=kwargs.get("message", None)

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
            **kwargs
    ):
        check_kwargs(
            parameter_list = ["module", "method", "exception", "status", "message", "logger", "verbose"],
            caller="ErrorHandler-log",
            **kwargs
        )

        module=kwargs.get("module", None)
        method=kwargs.get("method", None)
        exception=kwargs.get("exception", None)
        status=kwargs.get("status", None)
        message=kwargs.get("message", None)
        logger=kwargs.get("logger", None)
        verbose=kwargs.get("verbose", None)

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
