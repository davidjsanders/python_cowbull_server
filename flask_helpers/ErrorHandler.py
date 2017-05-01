import json
import logging
from flask import Response


class ErrorHandler:

    def __init__(self, **kwargs):
        pass

    def error(self, module=None, method=None, status=None, exception=None, message=None):
        response_dict = {
            "status": status or "NA",
            "module": module or "NA",
            "method": method or "NA",
            "exception": exception,
            "message": message or "No message was provided!"
        }

        print("Response dict: {}".format(response_dict))
        self.log(
            module=response_dict["module"],
            method=response_dict["method"],
            exception=response_dict["exception"],
            status=response_dict["status"],
            message="* {}".format(response_dict["message"])
        )

        return Response(
            mimetype="application/json",
            status=response_dict["status"],
            response=json.dumps(response_dict)
        )

    def log(self, module=None, method=None, exception=None, status=None, message=None):
        _message = "{}--{}--{}--{}--{}".format(
            module,
            method,
            status,
            exception,
            message
        )
        logging.debug(_message)
