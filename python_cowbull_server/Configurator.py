import json
import logging
import os
import sys

from flask_helpers.ErrorHandler import ErrorHandler
from flask_helpers.check_kwargs import check_kwargs
from flask import Flask
from Persistence.PersistenceEngine import PersistenceEngine


class Configurator(object):
    """
    Provides a configuration control to enable the Python Cowbull Server to execute_load
    configuration from a set of variables or from a configuration file.
    """

    def __init__(self):
        self.app = None
        self.configuration = {}
        self.error_handler = None
        default_config_file = "./python_cowbull_server/defaults.config"
        self.env_vars = self._load_defaults(default_config_file)

    def execute_load(self, app):
        if app is None:
            raise ValueError("The Flask app must be passed to the Configurator")
        if not isinstance(app, Flask):
            raise TypeError("Expected a Flask object, received {0}".format(type(app)))

        self.app = app
        self.app.config["PYTHON_VERSION_MAJOR"] = sys.version_info[0]

        self.app.config["LOGGING_FORMAT"] = os.getenv(
            "logging_format",
            os.getenv("LOGGING_FORMAT", "%(asctime)s %(levelname)s: %(message)s")
        )
        self.app.config["LOGGING_LEVEL"] = os.getenv(
            "logging_level",
            os.getenv("LOGGING_LEVEL", logging.WARNING)
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
        self.app.config["COWBULL_CONFIG"] = config_file

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
        return [
                   ("LOGGING_LEVEL", self.app.config["LOGGING_LEVEL"]),
                   ("LOGGING_FORMAT", self.app.config["LOGGING_FORMAT"]),
                   ("COWBULL_CONFIG", self.app.config["COWBULL_CONFIG"])
               ] \
               + \
               [(i["name"], self.app.config[i["name"]]) for i in self.env_vars]

    def print_variables(self):
        print('')
        print('=' * 80)
        print('=', ' '*30, 'CONFIGURATION', ' '*31, '=')
        print('=' * 80)
        print('The following environment variables may be set to dynamically configure the')
        print('server. Alternately, these can be defined in a file and passed using the env.')
        print('var. COWBULL_CONFIG. Please note, the file must be a JSON data object.')
        print('')
        print('Please note. Env. Var. names can be *ALL* lowercase or *ALL* uppercase.')
        print('')
        print('-' * 80)
        print('| Current configuration set:')
        print('-' * 80)
        for name, val in self.dump_variables():
            outstr = "| {:20s} | {}".format(name, val)
            print(outstr)
        print('-' * 80)
        print('')

    def load_variables(self, source=None):
        if source:
            _fetch = source.get
        else:
            _fetch = os.getenv

        for item in self.env_vars:
            self.error_handler.log(
                method="load_variables",
                message="Processing {} of type {}".format(
                    item.get("name", "no name provided"),
                    item.get("caster", "string")
                ),
                logger=logging.debug
            )
            if isinstance(item, dict):
                self.error_handler.log(
                    method="load_variables",
                    message="Item is a dict: {}".format(item.get("name", "unknown name")),
                    logger=logging.debug
                )
                self._set_config(
                    source=_fetch,
                    **item
                )
            elif isinstance(item, str):
                self.error_handler.log(
                    method="load_variables",
                    message="Item is a string: {}".format(item.get("name", "unknown name")),
                    logger=logging.debug
                )
                self._set_config(
                    name=item,
                    source=_fetch
                )
            elif isinstance(item, list):
                self.error_handler.log(
                    method="load_variables",
                    message="Item is a list: {}".format(item.get("name", "unknown name")),
                    logger=logging.debug
                )
                self.load_variables(source=item)
            else:
                raise TypeError("Unexpected item in configuration: {}, type: {}".format(item, type(item)))

    def _load_defaults(
            self,
            source
    ):
        if not source:
            raise ValueError("Source for _load_defaults is None!")

        f = None
        try:
            f = open(source, 'r')
            _defaults = json.load(f)
        except IOError:
            raise IOError("The source file for _load_defaults was not found!")
        finally:
            if f:
                f.close()

        _persister_default = {
            "engine_name" : "redis",
            "parameters": {
                "host": "{0}".format(_defaults["redis_host"]),
                "port": _defaults["redis_port"],
                "db": 0
            }
        }
        _persister = {
            "name": "PERSISTER",
            "description": "The persistence engine object",
            "required": False,
            "default": json.dumps(_persister_default),
            "caster": PersistenceEngine
        }
        _flask_host = {
            "name": "FLASK_HOST",
            "description": "For debug purposes, defines the Flask host. Default is all traffic *not* localhost",
            "required": False,
            "default": "{0}".format(_defaults["flask_host"])
        }
        _flask_port = {
            "name": "FLASK_PORT",
            "description": "For debug purposes, the port Flask should serve on. Default is 5000",
            "required": False,
            "default": _defaults["flask_port"],
            "caster": int
        }
        _flask_debug = {
            "name": "FLASK_DEBUG",
            "description": "For debug purposes, set Flask into debug mode.",
            "required": False,
            "default": _defaults["flask_debug"],
            "caster": bool
        }
        _cowbull_dry_run = {
            "name": "COWBULL_DRY_RUN",
            "description": "Do not run the server, simply report the configuration that would "
                            "be used to run it.",
            "required": False,
            "default": False,
            "caster": bool
        }
        _cowbull_custom_modes = {
            "name": "COWBULL_CUSTOM_MODES",
            "description": "A file which defines additional "
                            "modes to be defined in addition to the default modes. The "
                            "file must be a list of JSON objects containing mode "
                            "definitions. Each object must contain (at a minimum): mode, digits, and "
                            "priority",
            "required": False,
            "default": None,
            "caster": self._load_from_json
        }

        return [
            _persister,
            _flask_host,
            _flask_port,
            _flask_debug,
            _cowbull_dry_run,
            _cowbull_custom_modes
        ]


    # http://sonarqube:9000/project/issues?id=cowbull_server&issues=AWiRMKAZaAhZ-jY-ujHl&open=AWiRMKAZaAhZ-jY-ujHl
    def _set_config(
            self,
            **kwargs
    ):
        check_kwargs(
            parameter_list = ["source", "name", "description", "required", "default", "errmsg", "caster", "choices"],
            caller="Configurator-_set_config",
            **kwargs
        )
        source=kwargs.get("source", None)
        name=kwargs.get("name", None)
        description=kwargs.get("description", None)
        required=kwargs.get("required", None)
        default=kwargs.get("default", None)
        errmsg=kwargs.get("errmsg", None)
        caster=kwargs.get("caster", None)
        choices=kwargs.get("choices", None)

        self.error_handler.log(
            method="_set_config",
            message="In _set_config -- source: {}, name: {}, description: {}, required: {}, default: {}, errmsg: {}, caster: {}, choices: {}"
                .format(
                    source,
                    name,
                    description,
                    required,
                    default,
                    errmsg,
                    caster,
                    choices
                ),
            logger=logging.debug
        )
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

        self.error_handler.log(
            method="_set_config",
            message="Before casting: {}".format(value),
            logger=logging.debug
        )

        if value is None:
            value = default

        if caster:
            if caster == PersistenceEngine:
                if not isinstance(value, dict):
                    value = json.loads(str(value).replace("'", ""))
                value = caster(**value)
            elif caster == bool and isinstance(value, str):
                if value.lower() == "false":
                    value = False
                else:
                    value = True
            else:
                value = caster(value)

        self.error_handler.log(
            method="_set_config",
            message="After casting: {}".format(value),
            logger=logging.debug
        )

        if choices and value not in choices:
                raise ValueError(
                    errmsg or
                        "The configuration value for {}({}) is not in the list of choices: {}".format(
                        name,
                        value,
                        choices
                    )
                )

        self.app.config[name] = value
        self.error_handler.log(
            message="In _set_config Set app.config[{}] = {}"
                .format(
                    name,
                    value
                ),
            logger=logging.debug
        )
        return value

    def _load_from_json(self, json_file_name):
        if not json_file_name:
            return None

        f = None
        return_value = None

        try:
            f = open(json_file_name, 'r')
            return_value = json.load(f)
        except Exception as e:
            self.error_handler.error(
                module="Configurator.py",
                method="_load_from_json",
                status=500,
                exception=repr(e),
                message="An exception occurred!"
            )
            raise IOError(
                "A JSON file ({}) cannot be loaded. Exception: {}".format(
                    json_file_name,
                    repr(e)
                )
            )
        finally:
            if f:
                f.close()
        return return_value
