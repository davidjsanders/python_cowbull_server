import json
import logging
from flask import Response


class ErrorHandler:
    defaults = {}

    def __init__(self, **kwargs):
        self.defaults["module"] = kwargs.get("module", None)
        self.defaults["method"] = kwargs.get("method", None)

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
            _verbose = False
        else:
            _verbose = verbose

        if verbose:
            _message = "MODULE:{}({}) STATUS:{} MESSAGE:{} {}".format(
                module or self.defaults["module"],
                method or self.defaults["method"],
                status,
                message,
                "EXCEPTION:{}".format(exception) if exception is not None else ""
            )
        else:
            _message = "{}".format(message)

        logger(_message)
