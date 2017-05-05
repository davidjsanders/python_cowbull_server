# Initialization code. Placed in a separate Python package from the main
# app, this code allows the app created to be imported into any other
# package, module, or method.

import logging          # Import standard logging - for levels only
import os               # Import OS package
from flask import Flask # Import Flask


# Instantiate the Flask application as app
app = Flask(__name__)

# Configure the app. Initially, the app will try to read a configuration
# file specified in an OS env var called "COWBULL_CONFIG". If the env
# var is not set, then it will default to "config/cowbull.cfg". Flask's
# configuration utilities will then try to read the file and process
# the config; if the file does not exist, then the FileNotFoundError
# exception will be raised and the configurator will look for individual
# env vars or set default values.
try:
    app.config.from_pyfile(os.environ.get("COWBULL_CONFIG", "config/cowbull.cfg"))
except FileNotFoundError:
    # In the exception, no configuration file was found, so revert back
    # to env vars. If the env vars aren't set, then default values are used.

    # Set the logging format and logging level. Note if these are set as env
    # vars, then they must be set as integer values. See
    # https://docs.python.org/3/library/logging.html#levels for more info.
    app.config["LOGGING_FORMAT"] = os.getenv(
        "LOGGING_FORMAT",
        "%(asctime)s %(levelname)s: %(message)s"
    )
    app.config["LOGGING_LEVEL"] = os.getenv("LOGGING_LEVEL", logging.INFO)
    try:
        # Env vars will be strings; so, the variable must be cast to an
        # int.
        app.config["LOGGING_LEVEL"] = int(app.config["LOGGING_LEVEL"])
    except ValueError:
        # If the variable could not be cast, then default to INFO (20)
        app.config["LOGGING_LEVEL"] = logging.INFO

    # If the app is being run in dev/test mode using Flask as the
    # webserver, the three variables will be defined for the host, port,
    # and debug (True/False) state. The host should be 0.0.0.0 if the
    # app is being run through Docker, otherwise localhost or 127.0.0.1
    # will work okay.
    app.config["FLASK_HOST"] = os.getenv("FLASK_HOST", "0.0.0.0")
    app.config["FLASK_PORT"] = os.getenv("FLASK_PORT", 5000)
    app.config["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG", True)

    # The env var will be a string, so it needs to be translated into a
    # bool. A cast cannot be used as any non-empty string equates to
    # a true. The env var is only checked for false, everything else
    # equates to True.
    if isinstance(app.config["FLASK_DEBUG"], str):
        if app.config["FLASK_DEBUG"].lower() == "false":
            app.config["FLASK_DEBUG"] = False
        else:
            app.config["FLASK_DEBUG"] = bool(app.config["FLASK_DEBUG"])

    # Set the game version for the app. This is a key env var as it
    # defines the url for the game. EG, if it was set to v1_32, then
    # the URL for game would be http://.../v1_32/game
    app.config["GAME_VERSION"] = os.getenv("GAME_VERSION", "v0_1")

    # Configure the connection information for redis; note - no checking
    # takes place at configuration time, only when a Redis request is
    # executed.
    app.config["REDIS_HOST"] = os.getenv("REDIS_HOST", "redis")
    app.config["REDIS_PORT"] = os.getenv("REDIS_PORT", 6379)
    app.config["REDIS_DB"] = os.getenv("REDIS_DB", 0)

    # Use Redis authentication is currently ignored
    app.config["REDIS_USEAUTH"] = False
