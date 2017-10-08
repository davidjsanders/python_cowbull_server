import json
import logging
import os
import sys

from flask_helpers.ErrorHandler import ErrorHandler
from flask import Flask


class Configurator(object):
    """
    Provides a configuration control to enable the Python Cowbull Server to execute_load
    configuration from a set of variables or from a configuration file.
    """

    def __init__(self):
        self.app = None
        self.configuration = {}
        self.error_handler = None
        self.env_vars = [
            {
                "name": "REDIS_HOST",
                "description": "The Redis host name, e.g. redis.myredishost.com",
                "required": True,
                "default": "localhost",
                "errmsg": "Redis host must be defined in the OS Env. Var. REDIS_HOST"
            },
            {
                "name": "REDIS_PORT",
                "description": "The Redis port, defaults to 6379",
                "required": False,
                "default": 6379,
                "caster": int
            },
            {
                "name": "REDIS_DB",
                "description": "The Redis database number, defaults to 0",
                "required": False,
                "default": 0,
                "caster": int
            },
            {
                "name": "REDIS_AUTH_ENABLED",
                "description": "A boolean indicator to state whether Redis authentication is enabled",
                "required": False,
                "default": False,
                "caster": bool
            },
            {
                "name": "FLASK_HOST",
                "description": "For debug purposes, defines the Flask host. Default is 0.0.0.0",
                "required": False,
                "default": "0.0.0.0"
            },
            {
                "name": "FLASK_PORT",
                "description": "For debug purposes, the port Flask should serve on. Default is 5000",
                "required": False,
                "default": 5000,
                "caster": int
            },
            {
                "name": "FLASK_DEBUG",
                "description": "For debug purposes, set Flask into debug mode.",
                "required": False,
                "default": True,
                "caster": bool
            }
        ]

    def execute_load(self, app):
        if app is None:
            raise ValueError("The Flask app must be passed to the Configurator")
        if not isinstance(app, Flask):
            raise TypeError("Expected a Flask object")

        self.app = app
        self.app.config["PYTHON_VERSION_MAJOR"] = sys.version_info[0]

        self.app.config["LOGGING_FORMAT"] = os.getenv(
            "logging_format",
            os.getenv("LOGGING_FORMAT", "%(asctime)s %(levelname)s: %(message)s")
        )
        self.app.config["LOGGING_LEVEL"] = os.getenv(
            "logging_level",
            os.getenv("LOGGING_LEVEL", None)
        )

        self.error_handler = ErrorHandler(
            module="Configurator",
            method="__init__",
            level=self.app.config["LOGGING_LEVEL"],
            format=self.app.config["LOGGING_FORMAT"]
        )

        self.error_handler.log(
            message="Initialized logging (level: {}, format: {})"
                .format(
                    self.app.config["LOGGING_LEVEL"],
                    self.app.config["LOGGING_FORMAT"]
                ),
            logger=logging.info
        )

        self.error_handler.log(message="Configuring environment variables.", logger=logging.info)

        self.configuration = {}

        config_file = self._set_config(
            source=os.getenv,
            name="COWBULL_CONFIG"
        )

        self.error_handler.log(
            message="Loading configuration from: {}".format(
                config_file if config_file else "environment variables"
            )
        )

        source = {}
        if config_file:
            _file = open(config_file, 'r')
            try:
                source = json.load(_file)
            except:
                raise
            finally:
                _file.close()

        self.load_variables(source=source)
        self.dump_variables()

    def get_variables(self):
        return [
                   ("LOGGING_LEVEL", "An integer representing the Python "
                                     "logging level (e.g. 10 for debug, 20 for warning, etc.)"),
                   ("LOGGING_FORMAT", "The format for logs. The default is >> "
                                      "%(asctime)s %(levelname)s: %(message)s"),
                   ("COWBULL_CONFIG", "A path and filename of a configuration file "
                                     "used to set env. vars. e.g. /path/to/the/file.cfg")
               ]\
               + [(i["name"], i["description"]) for i in self.env_vars]

    def dump_variables(self):
        for item in self.env_vars:
            self.error_handler.log(
                method="Config Variable",
                message="{}={}".format(item["name"], self.app.config[item["name"]])
            )

    def load_variables(self, source=None):
        if source:
            _fetch = source.get
        else:
            _fetch = os.getenv

        for item in self.env_vars:
            if isinstance(item, dict):
                self._set_config(
                    source=_fetch,
                    **item
                )
            elif isinstance(item, str):
                self._set_config(
                    name=item,
                    source=_fetch
                )
            elif isinstance(item, list):
                self.load_variables(source=item)
            else:
                raise TypeError("Unexpected item in configuration: {}, type: {}".format(item, type(item)))

    def _set_config(
            self,
            source=None,
            name=None,
            description=None,
            required=None,
            default=None,
            errmsg=None,
            caster=None
    ):
        value = source(
            name.lower(),
            source(name.upper(), None)
        )

        if required and value is None and default is None:
            raise ValueError(
                errmsg or
                "Problem fetching config item: "
                "{}. It is required and was not found or the value was None.".format(name)
            )

        if value is None:
            value = default

        if caster:
            value = caster(value)

        self.app.config[name] = value
        return value
