import os
import logging
import sys
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
            },
            {
                "name": "LOGGING_FORMAT",
                "required": False,
                "default": "%(asctime)s %(levelname)s: %(message)s"
            },
            {
                "name": "LOGGING_LEVEL",
                "required": False,
                "default": logging.DEBUG,
                "caster": int
            }
        ]

        config_file = self._get_from_env_var("COWBULL_CONFIG")
        if config_file:
            self.load_from_file(config_file)
        else:
            self.load_from_iterable()

    def load_from_file(self, filename):
        #TODO Implement file IO for config
        raise NotImplemented("Work in progress!")

    def load_from_iterable(self, env_var_iterable=None):
        _list = env_var_iterable or self.env_vars

        for item in _list:
            if isinstance(item, dict):
                self._set_config(
                    value=self._get_from_env_var(item["name"]),
                    **item
                )
            elif isinstance(item, str):
                self._set_config(
                    name=item,
                    value=self._get_from_env_var(item)
                )
            elif isinstance(item, list):
                self.load_from_iterable(item)
            else:
                raise TypeError("Unexpected item in configuration: {}, type: {}".format(item, type(item)))

    def _get_from_env_var(
            self,
            name=None
    ):
        value = os.getenv(
            name.lower(),
            os.getenv(name.upper(), None)
        )
        return value

    def _set_config(
            self,
            name=None,
            value=None,
            required=None,
            default=None,
            errmsg=None,
            caster=None
    ):
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
