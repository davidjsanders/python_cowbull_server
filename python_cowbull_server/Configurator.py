import json
import logging
import os
import sys

from flask_helpers.ErrorHandler import ErrorHandler
from flask import Flask


class Configurator(object):
    """
    Provides a configuration control to enable the Python Cowbull Server to load
    configuration from a set of variables or from a configuration file.
    """

    def __init__(self, app):
        if app is None:
            raise ValueError("The Flask app must be passed to the Configurator")
        if not isinstance(app, Flask):
            raise TypeError("Expected a Flask object")

        self.app = app

        app.config["PYTHON_VERSION_MAJOR"] = sys.version_info[0]

        app.config["LOGGING_FORMAT"] = os.getenv(
            "logging_format",
            os.getenv("LOGGING_FORMAT", "%(asctime)s %(levelname)s: %(message)s")
        )
        app.config["LOGGING_LEVEL"] = int(os.getenv(
            "logging_level",
            os.getenv("LOGGING_LEVEL", logging.DEBUG)
        ))

        self.error_handler = ErrorHandler(
            module="Configurator",
            method="__init__",
            level=app.config["LOGGING_LEVEL"],
            format=app.config["LOGGING_FORMAT"]
        )

        self.error_handler.log(
            message="Initialized logging (level: {}, format: {})"
                .format(
                    app.config["LOGGING_LEVEL"],
                    app.config["LOGGING_FORMAT"]
                ),
            logger=logging.info
        )

        self.error_handler.log(message="Configuring environment variables.", logger=logging.info)

        self.configuration = {}
        self.env_vars = [
            {
                "name": "REDIS_HOST",
                "required": True,
                "default": None,
                "errmsg": "Redis host must be defined in the OS Env. Var. REDIS_HOST"
            },
            {
                "name": "REDIS_PORT",
                "required": False,
                "default": 6379,
                "caster": int
            },
            {
                "name": "REDIS_DB",
                "required": False,
                "default": 0,
                "caster": int
            },
            {
                "name": "REDIS_AUTH_ENABLED",
                "required": False,
                "default": False,
                "caster": bool
            },
            {
                "name": "FLASK_HOST",
                "required": False,
                "default": "0.0.0.0"
            },
            {
                "name": "FLASK_PORT",
                "required": False,
                "default": 5000,
                "caster": int
            },
            {
                "name": "FLASK_DEBUG",
                "required": False,
                "default": True,
                "caster": bool
            }
        ]

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
            required=None,
            default=None,
            errmsg=None,
            caster=None
    ):
        value = source(
            name.lower(),
            source(name.upper(), None)
        )

        if required and value is None:
            raise ValueError(
                errmsg or
                "Problem fetching config item: {}. It is required and was not found or the value was None.".format(name)
            )

        if value is None:
            value = default

        if caster:
            value = caster(value)

        self.app.config[name] = value
        return value
